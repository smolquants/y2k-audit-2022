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

- Seller deposits $1M of ETH in the risk vault to underwrite the depeg insurance
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


## Size Not Known at Time of Purchase

The amount of insurance purchased (payout size) by the hedge vault depositor $i$ with $B_i$ of collateral is variable and depends on the other
hedge buyers that may come in after the purchaser $k > i$ given the pro-rata payout structure. Therefore, the size the buyer is covered
for is not actually known to the buyer at the time of purchase. Usually with insurance products (and options), the purchaser of the
coverage buys the contracts for a known fixed coverage size.

A three-player example to illustrate:

- Seller deposits $1M of ETH in the risk vault to underwrite the depeg insurance
- Buyer 1 deposits $10 of ETH in the hedge vault to buy depeg insurance
- Buyer 2 deposits $90 of ETH in the hedge vault after buyer 1 to also buy depeg insurance
- If depeg occurs, buyer 1 receives $100K and buyer 2 receives $900K.
- If buyer 2 had not purchased insurance after buyer 1, buyer 1 would have received $1M.

This becomes a real problem when a trader uses the purchased insurance as a hedge for a fixed
amount of stablecoins held in their portfolio, as the hedge has been significantly reduced due to demand
from other buyers purchasing *after* them -- from $1M to $100K in the case of buyer 1 in the three-player example.

Another way to realize this is by examining the pro-rata depeg event payout $(B_i/B) \cdot S$. Per-unit of risk vault
collateral for the payout should be the number of contracts buyer $i$ purchased of the binary put:

```math
\mathrm{OI} = \frac{B_i}{\sum_k B_k}
```

The sum $\sum_k B_k$ in the denominator of the open interest expression increases the more other buyers buy insurance.
Therefore, the open interest of buyer $i$ decreases significantly the more insurance is purchased by other buyers after $i$.
Ideally, $i$ should be able to purchase a fixed amount of open interest/coverage tokens that represent a fixed portion of the claim
on the total payout amount $S$. The initial purchase price for the option would need to be set higher than a starting ask price
of 0 for this to work (see prior issue).


## Recommendations for Pricing Mechanisms

Consider relying on an AMM with a price curve for the next iteration of the protocol. Y2K does currently
enable price discovery for the binary puts during the deposit period, but it's difficult to overcome the issues above
when taking the current pro-rata approach to price discovery.

A helpful reference example may be the [Squeeth approach](https://github.com/opynfinance/squeeth-monorepo), where option sellers collateralize and mint
the derivative token separately from the act of actually selling the option to buyers. Instead, selling occurs through sellers providing liquidity for
the minted option token on Uniswap vs ETH. The derivative vs ETH Uniswap pool is initialized with a suitable initial price by the first minters.

A possible alternative to the Squeeth approach of piggybacking on Uniswap to make a market for the binary put would be a specialized Y2K AMM
for the binary option. Risk vault depositors would collateralize and mint the derivative token for a given fixed size, then subsequently provide liquidity vs ETH
to the specialized AMM for buyers to then purchase insurance from the liquidity pool (eliminates the hedge vault).
The Y2k price curve should ultimately look similar in shape to the expected CDF (bound between 0 and 1 per unit of risk vault collateral), as this is what
traders are trading. Pool initializers must also be able to set a suitable initial price at pool deployment.
