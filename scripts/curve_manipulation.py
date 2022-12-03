import click
import numpy as np
import pandas as pd

from ape import Contract, accounts, chain, project
from ape.contracts import ContractInstance
from ape.api.accounts import AccountAPI


PRECISION = 10**18
FEE_PRECISION = 10**10
NUM_SIMS = 250


def mim_curve_pool() -> ContractInstance:
    return Contract("0x5a6A4D54456819380173272A5E8E9B9904BdF41B")


def crv3_curve_pool() -> ContractInstance:
    return Contract("0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7")


def deploy_mock_token(
    name: str,
    symbol: str,
    acc: AccountAPI,
) -> ContractInstance:
    return project.MockToken.deploy(name, symbol, sender=acc)


def deploy_mock_pool(
    actual_pool: ContractInstance,
    mock_token0: ContractInstance,
    mock_token1: ContractInstance,
    mock_lp: ContractInstance,
    acc: AccountAPI,
) -> ContractInstance:
    """
    Configures and deploys new mock pool with mock tokens
    """
    A = actual_pool.A()
    fee = actual_pool.fee()
    admin_fee = actual_pool.admin_fee()
    return project.MockStableSwapPool.deploy(
        acc.address,  # make sender the owner
        [mock_token0.address, mock_token1.address],
        mock_lp.address,
        A,
        fee,
        admin_fee,
        sender=acc,
    )


def mint_liquidity_to_mock_pool(
    actual_pool: ContractInstance,
    base_pool: ContractInstance,
    mock_pool: ContractInstance,
    mock_token0: ContractInstance,
    mock_token1: ContractInstance,
    acc: AccountAPI,
):
    """
    Mints liquidity to the mock pool replicating liquidity
    in the actual metapool.

    Assumes coin0 is MIM and coin1 is 3crv in the actual pool. Also,
    takes all coins in the base 3crv pool to be ~ 1 USD.
    """
    # calculate MIM balance in actual pool
    amount0 = actual_pool.balances(0)

    # calculate 3Crv balance in actual pool
    amount_base_lp = actual_pool.balances(1)
    base_lp_total_supply = Contract(actual_pool.coins(1)).totalSupply()

    # calculate USD balance in base pool assuming actual is a meta pool
    mock_token1_decimals = mock_token1.decimals()
    amount1 = 0
    for i in range(3):
        coin_decimals = Contract(base_pool.coins(i)).decimals()
        factor = 10 ** (mock_token1_decimals - coin_decimals)
        amount1 += (
            base_pool.balances(i) * amount_base_lp * factor
        ) // base_lp_total_supply

    # mint token amounts to acc prior to adding liquidity to mock pool
    mock_token0.mint(acc, amount0, sender=acc)
    mock_token1.mint(acc, amount1, sender=acc)

    # add the minted liquidity
    click.echo(f"Adding balances=[{amount0}, {amount1}] of liquidity to pool")
    mock_pool.add_liquidity([amount0, amount1], 0, sender=acc)


def get_marginal_price(
    mock_pool: ContractInstance,
    i: int,
    j: int,
) -> float:
    """
    Returns the current marginal price for the pool in units
    of <j> / <i> (as if selling i for j).

    j is the base, i is the quote.
    """
    dx = PRECISION  # 1
    fee_rate = mock_pool.fee() / FEE_PRECISION
    price_less_fees = mock_pool.get_dy(i, j, dx) / dx

    # return price prior to fee application
    return price_less_fees / (1 - fee_rate)


def simulate_swaps(
    mock_pool: ContractInstance,
    mock_token0: ContractInstance,
    mock_token1: ContractInstance,
    xps: np.ndarray,
    acc: AccountAPI,
) -> pd.DataFrame:
    """
    Generates simulated swap data on the mock pool for the given
    x amounts in.

    Order of events:
        1. Mints x amount of token0 to acc to prep for swap
        2. Swaps x through mock pool for y out. Records price
        3. Mints another y amount of token1 to acc to simulate arb back
        4. Swaps y through mock pool for x' out
        5. Swaps y again through mock pool for x'' out. Records price.
        6. Records x_out = x'' and final price.
        7. Reverts the chain for next simulated swap size in xs.
    """
    results = {
        'x_ins': [],
        'initial_prices': [],
        'reached_prices': [],  # price post first swap (attack target)
        'ys': [],  # y received post first swap
        'final_prices': [],
        'x_outs': [],  # amount out after two swaps
        'dxs': [],  # x_out - xin
    }
    df = pd.DataFrame(data=results)

    for i, xp in enumerate(xps):
        snapshot_id = chain.snapshot()

        x = int(xp * PRECISION)  # add the 10**18 decimals back in
        click.echo(f"Iteration {i} of {len(xps)}")
        click.echo(f"Simulating swap of size {x} ...")

        # get the initial price
        initial_price = get_marginal_price(mock_pool, 0, 1)

        # mint x sell size to acc
        mock_token0.mint(acc, x, sender=acc)

        # swap x through mock pool
        mock_token1_bal_prior = mock_token1.balanceOf(acc)
        mock_pool.exchange(0, 1, x, 0, sender=acc)
        y = mock_token1.balanceOf(acc) - mock_token1_bal_prior
        reached_price = get_marginal_price(mock_pool, 0, 1)

        # mint another y / (1 - fee_rate) to acc to simulate arb back
        fee_rate = mock_pool.fee() / FEE_PRECISION
        y_before_fees = int(y / (1 - fee_rate))
        mock_token1.mint(acc, y_before_fees, sender=acc)

        # swap y / (1 - fee_rate) through mock pool to sim an arb back
        mock_pool.exchange(1, 0, y_before_fees, 0, sender=acc)

        # swap y through rebalanced pool
        mock_token0_bal_prior = mock_token0.balanceOf(acc)
        mock_pool.exchange(1, 0, y, 0, sender=acc)
        x_out = mock_token0.balanceOf(acc) - mock_token0_bal_prior
        final_price = get_marginal_price(mock_pool, 0, 1)

        # append simulated results to dict
        df = df.append({
            'x_ins': xp,
            'initial_prices': initial_price,
            'reached_prices': reached_price,
            'ys': y / PRECISION,
            'final_prices': final_price,
            'x_outs': x_out / PRECISION,
            'dxs': (x_out - x) / PRECISION,
        }, ignore_index=True)

        # revert the chain for all txs in loop to go again
        chain.restore(snapshot_id)

    return df


def main():
    """
    Deploys a new Curve pool using mock tokens to simulate
    price changes.

    Mock Curve pools parameters are set to be
    the same as the MIM Metapool.
    """
    # fake account to use for deployments
    acc = accounts.test_accounts[0]

    # mim pool to replicate
    actual_pool = mim_curve_pool()

    # base 3crv pool to replicate
    base_pool = crv3_curve_pool()

    # mock ERC20 tokens needed for pool
    click.echo("Deploying mock tokens ...")
    mock_token0 = deploy_mock_token("Mock MIM", "MMIM", acc)
    mock_token1 = deploy_mock_token("Mock USD", "MUSD", acc)
    mock_lp = deploy_mock_token("Mock LP", "MLP", acc)

    # deploy mock curve pool
    click.echo("Deploying mock pool ...")
    mock_pool = deploy_mock_pool(
        actual_pool,
        mock_token0,
        mock_token1,
        mock_lp,
        acc,
    )

    # approve mock pool to transfer coins
    mock_token0.approve(mock_pool.address, 2**256 - 1, sender=acc)
    mock_token1.approve(mock_pool.address, 2**256 - 1, sender=acc)

    # add liquidity in proportion to mim pool
    click.echo("Minting liquidity to mock pool ...")
    mint_liquidity_to_mock_pool(
        actual_pool, base_pool, mock_pool, mock_token0, mock_token1, acc
    )
    mock_lp_balance = mock_lp.balanceOf(acc)
    click.echo(f"Curve pool minted {mock_lp_balance} LP tokens to acc.")

    # get the current marginal price of pool at init
    # PRICE = <USD> / <MIM>
    price0 = get_marginal_price(mock_pool, 0, 1)
    click.echo(f"Marginal price of the pool prior to swaps: {price0}")

    # swap back and forth to trigger price changes for different sizes
    # recording dx_in, dx_out, price0 (init), price1 (after swap1),
    # price2 (after both swaps)
    click.echo("Simulating swap attack ...")
    dx = (mock_lp_balance / PRECISION) / NUM_SIMS
    xps = np.linspace(dx, mock_lp_balance / PRECISION, NUM_SIMS)
    df = simulate_swaps(
        mock_pool,
        mock_token0,
        mock_token1,
        xps,
        acc,
    )

    # print the results and save to csv
    click.echo(f"Swap attack results: {df}")
    df.to_csv("scripts/results/curve_manipulation.csv")
