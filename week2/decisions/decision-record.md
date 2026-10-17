# Week 2 Decision Record

**Case:** a $60/day AWS line item. Today's cost is ≥3× its 7-day median, usage rose with it (no price-per-unit jump), the region was used before, and the resource has **no owner tag**.
The true cause is **unknown** (this is a constructed example, not a labelled case).
All numbers are produced by `src/model.py` / `src/policies.py` (policy **P3c**) and reproduced in `results/analysis.md`. All probabilities and costs are **hypothetical** unless marked *measured*.

---

## 1. Hidden states, prior, and where the prior came from

| Hidden state | Meaning | Prior | Origin |
|---|---|---|---|
| Normal | ordinary variation | 0.78 | judgement (Week 1: 0.80, minus 0.02 for Other) |
| Planned | a job someone planned (batch, load test, launch) | 0.08 | judgement (unchanged from Week 1) |
| Waste | forgotten resource, retry loop, misconfiguration | 0.07 | judgement (Week 1: 0.08) |
| Compromise | leaked keys, attacker spending | 0.03 | judgement (Week 1: 0.04) |
| Other (residual) | price change, expired discount, billing correction, anything else | 0.04 | added after Week 1 failure F6 and review Q6 |
| **Sum** | | **1.00** | |

## 2. Evidence, step by step (free evidence first)

| Step | Normal | Planned | Waste | Compromise | Other | Entropy (bits) |
|---|---|---|---|---|---|---|
| Prior | 0.780 | 0.080 | 0.070 | 0.030 | 0.040 | 1.177 |
| spike = high | 0.517 | 0.199 | 0.116 | 0.124 | 0.044 | **1.889** ↑ |
| price jump = no | 0.523 | 0.212 | 0.124 | 0.133 | 0.007 | 1.777 |
| region = seen before | 0.574 | 0.233 | 0.136 | 0.049 | 0.009 | 1.613 |
| owner tag = **untagged** | 0.293 | 0.179 | 0.313 | 0.211 | 0.005 | **1.996** ↑ |

Each row sums to 1.00 (rounding). Entropy goes **up** twice: the agent learns something, but moves from "probably normal" to "something is going on, but I don't know what."

### The first update worked by hand

| State | Prior | P(high spike given state) | Prior × likelihood | Posterior |
|---|---|---|---|---|
| Normal | 0.78 | 0.12 *(measured, Week 1 data)* | 0.0936 | 0.0936 / 0.1811 = **0.517** |
| Planned | 0.08 | 0.45 | 0.0360 | **0.199** |
| Waste | 0.07 | 0.30 | 0.0210 | **0.116** |
| Compromise | 0.03 | 0.75 | 0.0225 | **0.124** |
| Other | 0.04 | 0.20 | 0.0080 | **0.044** |
| Sum | 1.00 | | 0.1811 = P(high spike) | 1.000 |

## 3. What to do now? (expected cost after free evidence)

| Action | Expected cost |
|---|---|
| Ignore | $1,179.9 |
| **Report** | **$162.8** ← best now |
| Limit | $397.2 |

## 4. Which evidence next?

| Paid check | Price | Time | Exp. info gain | Net value of information | Can it change the action? |
|---|---|---|---|---|---|
| **launcher (CloudTrail)** | $1 | 1 min | 0.244 bits | **+$55.0** | yes |
| ticket | $5 | 5 min | 0.274 bits | −$5.9 | no |
| ask_owner | $40 | 2 h | 0.522 bits | +$13.3 | yes |
| forensics | $2,000 | 48 h | **0.628 bits** (most) | **−$2,414.2** | yes |

**The agent buys the launcher check:** it has positive value, and the most information per dollar (20.7 bits per $100). Forensics carries the most information and is by far the worst purchase.

## 5. New evidence arrives: launcher = unknown

| | Normal | Planned | Waste | Compromise | Other | Entropy |
|---|---|---|---|---|---|---|
| Before | 0.293 | 0.179 | 0.313 | 0.211 | 0.005 | 1.996 |
| P(unknown given state) | 0.05 | 0.05 | 0.15 | 0.70 | 0.05 | |
| **After** | 0.067 | 0.041 | 0.215 | **0.676** | 0.001 | 1.319 |

Expected costs now: Ignore $3,466.6, Report $419.7, **Limit $162.3**. Limit is cheapest, but P(Compromise) = 0.676 is **below the 0.7 guard**, so the agent may not Limit on its own yet.

Remaining checks: **ticket +$25.0** (can change the action), ask_owner −$48.9, forensics −$3,479.6. The agent buys the ticket check.

## 6. Policy, threshold, and stop rule

- **Decision rule:** choose the action with the lowest expected cost.
- **Thresholds (derived from costs, at $60/day):** Ignore → Report when P(Compromise) > 50/(50+4,400) = **1.1%**; Report → Limit when P(Compromise) > **33%** (if the alternative is Normal) to **74%** (if it is Planned). The 1.1% falls with the bill: 0.15% at $1,000/day.
- **Human control:** automatic Limit only if P(Compromise) ≥ **0.7** and the bill is under **$3,000/day**; otherwise a human decides (Report).
- **Stop rule:** stop buying when no remaining check has positive value of information, when two checks in a row move the belief by less than 0.02, or after 4 paid checks.

## 7. Decision

| If the ticket says | Belief after | Action | Why |
|---|---|---|---|
| **none** | Compromise **0.710** | **Limit** | Above the 0.7 guard; no remaining check is worth its cost |
| **found** | Compromise 0.356, Planned 0.345, Waste 0.226 (entropy **1.831**, up from 1.319) | **Report** | The ticket splits the belief between Planned and Compromise. The agent then asks the owner ($40, value +$64.2). If the owner says "intended" → Planned 0.719, Report. If "not intended" → Compromise 0.622, still below 0.7 → Report to a human |

## 8. Audit data

| Item | Value |
|---|---|
| Decision time | 2026-10-17 (IST) |
| Data | `data/aws_billing_data_mock.csv`, SHA-256 prefix `8f95baffbe87f824` (same file as Week 1) |
| Model version | `w2-model-1.0` (`src/model.py`) |
| Policy version | P3c = P3 + stakes-dependent costs + Limit guard 0.7 (`src/policies.py`) |
| Code version | Git commit of this file |
| Simulation seeds (experiments) | main 42; robustness 100–119 |
