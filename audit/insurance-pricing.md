# Insurance Pricing

Insurance pricing mechanism analysis.


## Background

Y2K currently offers binary option markets on depeg events for the stablecoins

- MIM: `K = 0.9759`
- USDC: `K = 0.9979`
- USDT: `K = 0.9919`
- FRAX: `K = 0.9909`
- DAI: `K = 0.9969`

paired against USD, with strike `K` specified for each market.

The protocol has two sets of vaults, hedge and risk, that buyers and sellers
of the option, respectively, can deposit capital into during an initial deposit period.
This deposit phase is where price discovery happens for the value of the Y2K binary
put on the stablecoin depeg.

Once deposited, users are *not* able to withdraw their capital until either after expiry
or once a depeg event is triggered (i.e. price goes below strike $K$).

Expressions for the rest of the insurance pricing mechanism follow those of the
[Y2K whitepaper](https://www.docdroid.net/7zgCd3R/y2k-whitepaper-pdf) with additions:

- $B = \sum_i B_i$ is the total premiums paid by hedge vault depositors
- $S = \sum_j S_j$ is the total collateral posted by risk vault depositors


## Quoting the Put with Zero Hedgers




## Price Not Known at Time of Purchase


