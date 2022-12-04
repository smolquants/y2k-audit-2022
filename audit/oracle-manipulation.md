# Oracle Manipulation

Oracle manipulation analysis.


## Background

Y2K currently offers binary option markets on depeg events for the stablecoins

- MIM: `K = 0.9759`
- USDC: `K = 0.9979`
- USDT: `K = 0.9919`
- FRAX: `K = 0.9909`
- DAI: `K = 0.9969`

paired against USD, with strike `K` specified for each market.

MIM is likely the riskiest of all markets offered, reflected in the lower strike
price set by the protocol.

Focus for the oracle manipulation analysis was on MIM given the increased risks
to option sellers of this market.


## Risks with the MIM Curve Metapool

Users of Abracadbra can mint MIM through a CDP mechanism, with the loan
backed by various collateral types. Analytics dashboards for MIM are provided
by Abracadabra:

- [Overview](https://analytics.abracadabra.money/overview)
- [Cauldrons](https://analytics.abracadabra.money/cauldrons)

breaking down outstanding supply, borrows, collateral, and collateral profile.

An overview as of 2022-12-04,

- ~85M MIM of total borrows (i.e. MIM circulating supply)
- ~154M USD worth of collateral backing

with the majority of activity (~97.5%) on Ethereum mainnet.

However the top holders of MIM on Ethereum are heavily concentrated
in a few addresses, with **~62% of the circulating supply in the MIM Curve Metapool**.

To understand the liquidity distirbution of MIM, several relevant top
holders from [Etherscan's MIM Token page](https://etherscan.io/token/tokenholderchart/0x99d8a9c45b2eca8864373a26d1459e3dff1e17f3)
are listed below:

1. 472.016M in anyMIM contract
2. 115.069M in a [“CauldronOwner” contract](https://etherscan.io/address/0x30b9de623c209a42ba8d5ca76384ead740be9529)
3. 53.217M in [Curve Metapool with MIM and 3Crv](https://etherscan.io/address/0x5a6a4d54456819380173272a5e8e9b9904bdf41b)
4. 30.724M in [Abracadabra Multisig](https://etherscan.io/address/0x5f0dee98360d8200b20812e174d139a1a633edd2)
5. 5.892M in [Abracadabra Degenbox](https://etherscan.io/address/0xd96f48665a1410c0cd669a88898eca36b9fc2cce#code)
6. 1.290M in a single [EOA](https://zapper.fi/account/0xd7efcbb86efdd9e8de014dafa5944aae36e817e4)
7. 0.795M in Sushiswap [BentoBox V1](https://etherscan.io/address/0xf5bce5077908a1b7370b9ae04adc565ebd643966)
8. 0.688M in [Gemini 4](https://etherscan.io/address/0x5f65f7b609678448494de4c87521cdf6cef1e932)
15. 0.200M in [Bitfinex: Hot Wallet](https://etherscan.io/address/0x77134cbc06cb00b66f4c7e623d5fdbf6777635ec)
16. 0.183M in [SushiSwap: MIM 2 Pool (MIM/WETH)](https://etherscan.io/address/0x07d5695a24904cc1b6e3bd57cc7780b90618e3c4)
20. 0.022M in [Uni V3: MIM-USDC Pool](https://etherscan.io/address/0x298b7c5e0770d151e4c5cf6cca4dae3a3ffc8e27)

As the majority of the liquidity for MIM lies in the single Curve metapool,
price discovery for MIM vs USD will likely happen through this pool. This
is a significant risk for Y2K when offering markets on MIM, as price manipulation
of this lone pool by a large MIM holder will likely be difficult to arbitrage
back due to insignificant liquidity on other major DEXs and CEXs.


## Manipulating the Curve Pool to Trigger Depegs


## Mitigating Curve Pool Attacks