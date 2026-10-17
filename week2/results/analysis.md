# Worked analysis (all numbers computed by experiments/run_analysis.py)

All probabilities and costs are HYPOTHETICAL unless marked measured (see src/model.py).

## 1. Belief-state table for one example case

Example evidence: {'spike': 'high', 'price_jump': 'no', 'region_new': 'seen', 'owner_tag': 'untagged'} (a $60/day line item).

| Step | Normal | Planned | Waste | Compromise | Other | Entropy (bits) |
|---|---|---|---|---|---|---|
| prior | 0.780 | 0.080 | 0.070 | 0.030 | 0.040 | 1.177 |
| after spike = high | 0.517 | 0.199 | 0.116 | 0.124 | 0.044 | 1.889 |
| after price_jump = no | 0.523 | 0.212 | 0.124 | 0.133 | 0.007 | 1.777 |
| after region_new = seen | 0.574 | 0.233 | 0.136 | 0.049 | 0.009 | 1.613 |
| after owner_tag = untagged | 0.293 | 0.179 | 0.313 | 0.211 | 0.005 | 1.996 |

Implied action after free evidence: **Report** (expected costs: Ignore $1,179.9, Report $162.8, Limit $397.2)

### One update worked in full: prior -> after 'spike = high'

| State | Prior | P(high spike given state) | Prior x likelihood | Posterior |
|---|---|---|---|---|
| Normal | 0.78 | 0.12 | 0.0936 | 0.517 |
| Planned | 0.08 | 0.45 | 0.0360 | 0.199 |
| Waste | 0.07 | 0.30 | 0.0210 | 0.116 |
| Compromise | 0.03 | 0.75 | 0.0225 | 0.124 |
| Other | 0.04 | 0.20 | 0.0080 | 0.044 |
| **Sum** | 1.00 | | **0.1811** = P(high spike) | 1.000 |

## 2. Which evidence next? (starting from the belief after free evidence)

Belief: Normal 0.293, Planned 0.179, Waste 0.313, Compromise 0.211, Other 0.005; entropy 1.996 bits.

| Evidence | Exp. info gain (bits) | Price | Time | Delay loss | Bits per $100 | Net value of info | Can change action? |
|---|---|---|---|---|---|---|---|
| launcher | 0.244 | $1 | 1 min | $0.18 | 20.72 | $55.0 | yes |
| ticket | 0.274 | $5 | 5 min | $0.89 | 4.65 | $-5.9 | no |
| ask_owner | 0.522 | $40 | 2 h | $21.37 | 0.85 | $13.3 | yes |
| forensics | 0.628 | $2,000 | 48 h | $512.98 | 0.03 | $-2,414.2 | yes |

Outcome-by-outcome view (can a single result increase uncertainty?):

| Evidence | Outcome | P(outcome) | Entropy after | Change vs now |
|---|---|---|---|---|
| launcher | known | 0.782 | 1.873 | -0.123 |
| launcher | unknown | 0.218 | 1.319 | -0.677 |
| ticket | found | 0.215 | 1.428 | -0.568 |
| ticket | none | 0.785 | 1.803 | -0.194 |
| ask_owner | intended | 0.510 | 1.558 | -0.439 |
| ask_owner | not_intended | 0.490 | 1.388 | -0.608 |
| forensics | malicious | 0.216 | 0.364 | -1.632 |
| forensics | clean | 0.784 | 1.644 | -0.352 |

## 3. Five questions the agent could ask (values at the PRIOR, before any evidence)

| Question | Answers | Info value (bits) | Price | Time | Net value of info at prior |
|---|---|---|---|---|---|
| Does the resource have an owner/team tag? | tagged / untagged | 0.091 | $0.01 | 1 s | $2.3 |
| Does CloudTrail show a known person or pipeline launched it? | known / unknown | 0.063 | $1.00 | 1 min | $-1.0 |
| Is there a change ticket or deployment for this service today? | found / none | 0.136 | $5.00 | 5 min | $-5.1 |
| Does the owning team confirm this usage was intended? | intended / not_intended | 0.191 | $40.00 | 2 h | $-18.2 |
| Does a full security investigation find malicious activity? | malicious / clean | 0.152 | $2,000.00 | 48 h | $-2,056.0 |

## 4. Is the most informative question always the best?

### A. high spike, untagged, $60/day (example above)

Belief: Normal 0.293, Planned 0.179, Waste 0.313, Compromise 0.211, Other 0.005. Best action now: **Report** (expected cost $162.8).

| Check | Info gain (bits) | Net value of info | Changes action? |
|---|---|---|---|
| launcher | 0.244 | $55.0 | yes |
| ticket | 0.274 | $-5.9 | no |
| ask_owner | 0.522 | $13.3 | yes |
| forensics (most informative) | 0.628 | $-2,414.2 | yes |

### B. high spike, NEW region, untagged, $60/day

Belief: Normal 0.056, Planned 0.034, Waste 0.060, Compromise 0.849, Other 0.000. Best action now: **Limit** (expected cost $156.8).

| Check | Info gain (bits) | Net value of info | Changes action? |
|---|---|---|---|
| launcher | 0.155 | $-1.7 | no |
| ticket | 0.085 | $11.7 | yes |
| ask_owner | 0.256 | $-81.2 | yes |
| forensics (most informative) | 0.486 | $-3,869.5 | yes |

### C. med spike, untagged, $900/day (big bill)

Belief: Normal 0.385, Planned 0.134, Waste 0.430, Compromise 0.042, Other 0.009. Best action now: **Report** (expected cost $68.7).

| Check | Info gain (bits) | Net value of info | Changes action? |
|---|---|---|---|
| launcher | 0.080 | $-1.3 | no |
| ticket | 0.210 | $-6.6 | no |
| ask_owner (most informative) | 0.438 | $-79.5 | no |
| forensics | 0.195 | $-2,930.4 | yes |

### D. Searching for a case where the most informative check IS the best buy

I checked 600 situations (every free-evidence combination x 5 investigation histories x 5 bill sizes). The most informative remaining check was also the best purchase with positive value in only **2** of them (0.3%).

Example: {'spike': 'high', 'price_jump': 'no', 'region_new': 'seen', 'owner_tag': 'tagged', 'launcher': 'known'}, $60/day. Belief: Normal 0.652, Planned 0.250, Waste 0.084, Compromise 0.003, Other 0.010.

| Check | Info gain (bits) | Net value of info |
|---|---|---|
| ticket | 0.316 | $3.22 |
| ask_owner | 0.163 | $-8.00 |
| forensics | 0.018 | $-2,004.73 |

Here the confusion is between Normal and Planned, and the change ticket is the one check that separates exactly those two. It is the most informative AND worth buying, but only by a few dollars.

## 5. Thresholds derived from costs (two-state view, at $60/day)

- Ignore vs Report for Compromise: a false alarm costs $50; ignoring instead of reporting a compromise costs $5,000 - $600 = $4,400 more. Break-even P(Compromise) = 50 / (50 + 4,400) = **0.0112** (about 1.1%).
- Ignore vs Report for Waste: break-even P(Waste) = 50 / (50 + 360) = **0.122**.
- Report vs Limit for Compromise vs Normal: Limit saves $500 if Compromise and costs $250 extra if Normal. Break-even = 250 / (250 + 500) = **0.333**.
- Report vs Limit for Compromise vs Planned: Limit costs $1,450 extra if Planned. Break-even = 1,450 / (1,450 + 500) = **0.744**.
- So the uncertain band (Report) runs from about **1% to 33-74%** P(Compromise), depending on whether the alternative is Normal or Planned. The upper band is why a Planned job without a ticket is dangerous to Limit.

How the Ignore/Report break-even moves with the bill (stakes):

| Daily bill | Ignore cost if Compromise | Break-even P(Compromise) |
|---|---|---|
| $10 | $3,500 | 0.0169 |
| $60 | $5,000 | 0.0112 |
| $300 | $12,200 | 0.0043 |
| $1,000 | $33,200 | 0.0015 |
| $3,000 | $93,200 | 0.0005 |

## 6. Information measures with my numbers

- Entropy of the prior: 1.177 bits. Maximum possible for 5 states: 2.322 bits.
- Conditional entropy H(S | spike) = 1.006 bits, so I(S; spike) = 0.171 bits.
- Mutual information of each free signal with the hidden state, at the prior: spike 0.171, price_jump 0.090, region_new 0.046, owner_tag 0.091 bits.
- KL(posterior || prior) = 1.047 bits, but KL(prior || posterior) = 0.898 bits. Same two beliefs, different numbers: KL is not symmetric, so it is not a distance.
- Jensen-Shannon divergence between them = 0.223 bits (symmetric, between 0 and 1).
- If the true world has a 4% 'Other' state and my agent's list has none: KL(world || agent) is infinite (the agent gives zero probability to something that happens), while KL(agent || world) = 0.059 bits. JSD stays finite: 0.0203 bits. This is why the residual state matters and why JSD is used for alarms.

## 7. Umbrella problem (my own costs, in 'units of annoyance')

35% chance of rain in Mysuru tomorrow.

| | Case A: walk to the shop | Case B: client demo with my laptop |
|---|---|---|
| Cost of carrying it, no rain | 3 | 3 |
| Cost of getting wet | 6 | 400 (wet laptop, ruined demo) |
| Average cost if I carry it | 3.0 | 3.0 |
| Average cost if I don't | 0.35 x 6 = 2.1 | 0.35 x 400 = 140 |
| Break-even chance of rain | 3 / 6 = 0.50 | 3 / 400 = 0.0075 |
| Decision | Leave it (35% < 50%) | Take it (35% >> 0.75%) |

Same structure as the agent: rain = hidden state, umbrella = Report, getting wet = ignoring a compromise. Free sky check before leaving: if dark clouds raise rain to 70% and a clear sky drops it to 10% (hypothetical), in Case A the check can flip the decision (70% > 50%), so it has value; in Case B I take the umbrella either way (10% > 0.75%), so the check is worth nothing.
