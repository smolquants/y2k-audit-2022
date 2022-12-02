from ape import Contract, accounts
from ape.contracts import ContractInstance
from ape.project import MockStableSwapPool, MockToken
from ape.api.accounts import AccountAPI


def mim_curve_pool() -> ContractInstance:
    return Contract("0x5a6A4D54456819380173272A5E8E9B9904BdF41B")


def deploy_mock_token(
    name: str,
    symbol: str,
    acc: AccountAPI,
) -> ContractInstance:
    return MockToken.deploy(name, symbol, sender=acc)


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
    return MockStableSwapPool.deploy(
        acc.address,  # make sender the owner
        [mock_token0.address, mock_token1.address],
        mock_lp.address,
        A,
        fee,
        admin_fee,
        sender=acc
    )


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

    # mock ERC20 tokens needed for pool
    mock_token0 = deploy_mock_token("Mock MIM", "MMIM", acc)
    mock_token1 = deploy_mock_token("Mock DAI", "MDAI", acc)
    mock_lp = deploy_mock_token("Mock LP", "MLP", acc)

    # mock curve pool
    mock_pool = deploy_mock_pool(
        actual_pool,
        mock_token0,
        mock_token1,
        mock_lp,
        acc
    )
