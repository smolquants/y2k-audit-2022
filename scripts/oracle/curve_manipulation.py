from ape import Contract


def mim_curve_pool():
    yield Contract("0x5a6A4D54456819380173272A5E8E9B9904BdF41B")


def main():
    """
    Deploys a new Curve pool using mock tokens to simulate
    price changes.

    Mock Curve pools parameters are set to be
    the same as the MIM Metapool.
    """
    pass
