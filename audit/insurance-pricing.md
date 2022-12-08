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


### Payout Structure

Protocol fees are ignored for the sake of simplicity. Summary of the Y2K payout structure is below.

During the deposit phase,

- Buyer $i$ pays $B_i$ in premiums by depositing to the hedge vault
- Seller $j$ risks $S_j$ in collateral by depositing to the risk vault

If no depeg happens prior to expiry,

- Buyer $i$ receives zero payout
- Seller $j$ receives a pro-rata share of hedge vault premiums plus their original risk collateral back: $(S_j / S) \cdot B + S_j$

In the event of a depeg,

- Buyer $i$ receives a pro-rata share of risk vault collateral: $(B_i / B) \cdot S$
- Seller $j$ receives a pro-rata share of hedge vault premiums: $(S_j / S) \cdot B$


## Quoting the Put with Zero Hedgers

There is a significant mispricing of risk when the vaults first open due to the manner in which price discovery happens on Y2K.
The first buyer $i=0$ can bid whatever amount $B_0$ they want for the full rights to *all* of the collateral in the risk vault $S$
in the event of a depeg. The initial round of sellers are forced to sell at this price chosen by the first bidder given the mechanics
of the protocol.

A two-player example to illustrate:

- Seller deposits $1M of ETH in the risk vault ot underwrite the depeg insurance
- Buyer deposits $0.01 of ETH in the hedge vault to buy the depeg insurance *on $1M payout*
- If depeg occurs, buyer receives $1M and seller receives $0.01.

As the first binary put buyer is able to specify their own price through depositing whatever amount $B_0$ they desire,
the initial round of sellers depositing into the risk vault are effectively quoting the ask for the binary put at a
price of $0$. It is unlikely risk sellers actually are pricing the binary put at this value.

To prevent this scenario, sellers of the binary put should be able to specify an initial price
they're willing to sell at, similar to the price specified when e.g. initializing a Uniswap pool.


### Pricing the Binary Put

To dig a bit deeper into what quoting the ask implies, note that pricing the binary put is effectively
pricing the probability of a depeg event before expiry.

For simplicity, assume the puts are European (i.e. aren't triggered prior to expiry). The [market value for the binary put](https://en.wikipedia.org/wiki/Binary_option#Cash-or-nothing_put)
can be expressed as the discounted expectation of the future payoff under the risk-neutral measure $Q$:

```math
V(\tau) = S e^{-r \tau} \cdot \mathbb{E}_{Q}[\mathbb{1}_{P_{T} \leq K}] = S e^{-r \tau} \cdot \mathbb{P}_{Q}[P_{T} \leq K]
```

where

- $P_t$ is the price of the underlying stablecoin v.s. USD at time $t$
- $\tau$ is time to expiry
- $T$ is expiry time
- $r$ is the risk-free rate
- $S$ is the total collateral deposited in the risk vault
- $\mathbb{1}\_{P_{T} \leq K}$ is the indicator function

What Y2K vault depositors are trading when buying/selling the option $V(\tau)$ is the probability of
the depeg event $\mathbb{P}\_{Q}[P_{T} \leq K]$.

If sellers must honor an initial hedge vault depositor paying $B_0 \to 0$ with no other hedgers coming in after,
sellers are forced into expressing the view that the probability of a depeg event occurring within the epoch must be zero
$\mathbb{P}\_{Q}[P_{T} \leq K] \to 0$, simply due to the initial hedge vault depositor bidding a low price of 0.
This is particularly the case given vault depositors *cannot* withdraw their capital once deposited during the deposit period.


## Price Not Known at Time of Purchase


