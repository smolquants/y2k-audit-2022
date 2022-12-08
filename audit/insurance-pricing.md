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

Expressions for the rest of the insurance pricing mechanism analysis follow those of the
[Y2K whitepaper](https://www.docdroid.net/7zgCd3R/y2k-whitepaper-pdf) with additions:

- $B = \sum_i B_i$ is the total premiums paid by hedge vault depositors
- $S = \sum_j S_j$ is the total collateral posted by risk vault depositors

Protocol fees are ignored for the sake of simplicity.

Summary of the Y2K payout structure is below.

During the deposit phase,

- Buyer $i$ pays $B_i$ in premiums by depositing to the hedge vault
- Seller $j$ risks $S_j$ in collateral by depositing to the risk vault

If no depeg happens prior to expiry,

- Buyer $i$ receives zero payout
- Seller $j$ receives a pro-rata share of hedge vault premiums plus their original risk collateral back: $\frac{S_j}{S} \cdot B + S_j$

In the event of a depeg,

- Buyer $i$ receives a pro-rata share of risk vault collateral: $\frac{B_i}{B} \cdot S$
- Seller $j$ receives a pro-rata share of hedge vault premiums: $\frac{S_j}{S} \cdot B$


## Quoting the Put with Zero Hedgers




## Price Not Known at Time of Purchase


