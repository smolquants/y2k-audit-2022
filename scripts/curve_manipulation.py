import click

from ape import Contract, accounts, project
from ape.contracts import ContractInstance
from ape.api.accounts import AccountAPI


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
        sender=acc
    )


def mint_liquidity_to_mock_pool(
    actual_pool: ContractInstance,
    base_pool: ContractInstance,
    mock_pool: ContractInstance,
    mock_token0: ContractInstance,
    mock_token1: ContractInstance,
    acc: AccountAPI,
) -> int:
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
    amount1 = 0
    for i in range(3):
        amount1 += (base_pool.balances(i) * amount_base_lp) \
            // base_lp_total_supply

    # mint token amounts to acc prior to adding liquidity to mock pool
    mock_token0.mint(acc, amount0, sender=acc)
    mock_token1.mint(acc, amount1, sender=acc)

    # add the minted liquidity
    # TODO: fix
    receipt = mock_pool.add_liquidity([amount0, amount1], 0, sender=acc)
    return receipt.return_value


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
        acc
    )

    # add liquidity in proportion to mim pool
    click.echo("Adding minted liquidity to mock pool ...")
    minted_lp_amount = mint_liquidity_to_mock_pool(
        actual_pool,
        base_pool,
        mock_pool,
        mock_token0,
        mock_token1,
        acc
    )
    assert minted_lp_amount == mock_lp.balanceOf(acc)

    click.echo("mock_pool.balances:", [mock_pool.balances(i) for i in range(2)])
    click.echo("token.balanceOf(mock_pool):", [
        mock_token0.balanceOf(mock_pool),
        mock_token1.balanceOf(mock_pool),
    ])

    # TODO: check mock_pool.get_dy and do the actual swap to test slippage
    # TODO: and marginal price changes
