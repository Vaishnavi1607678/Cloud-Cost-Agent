# Probability Decision Record

**Case:** Lambda, 2025-07-10, ap-south-1, a **real, unmodified row** from `data/aws_billing_data_mock.csv`.
This row has **no label**, so its true state is unknown. It is the most expensive day in the whole dataset ($242.18).

All numbers below were computed with `src/agent_v2.py` (starting likelihoods, no learning) and checked by hand.

---

## Part 1 — Decision record

| Item | Information |
|---|---|
| **Evidence** | Today: 485.28 requests, **$242.18**, region ap-south-1. Last 7 days (Jul 3–9): costs $16.09, 28.04, 23.66, 108.42, 210.09, 37.21, 42.60 (median **$37.21**); usage median **249.30**; regions us-east-1, ap-south-1, us-west-2. **Cost ratio = 6.51× → "high" spike.** Usage ratio = 1.95×. The region **was seen before** (not new). |
| **Hidden states** | Normal, Planned, Waste, Compromise |
| **Beliefs** | Normal **36.2%**, Planned **32.6%**, Waste **21.7%**, Compromise **9.6%** (sum = 100%) |
| **Event** | "There is a real problem" = Waste **or** Compromise → P = **31.3%** |
| **Actions** | Ignore, Report (send to a human), Limit (budget action / throttle), Investigate ($25: CloudTrail launcher + change ticket) |
| **Costs** | See the table below |
| **Policy** | Choose the action with the **lowest expected cost**. Investigate first if the expected cost after investigating (+$25) is lower. Limit only if P(Compromise) ≥ 50% (human guard). |
| **Decision** | **Report.** Expected costs: Ignore $565.5, **Report $100.5**, Limit $619.4. A 9.6% compromise chance makes Ignore too risky, but it is too low to justify Limit. |
| **Audit data** | Decision time: 2026-10-17 (IST). Data: `aws_billing_data_mock.csv`, SHA-256 prefix `8f95baffbe87f824`. Model: likelihood tables v2.0 (starting values, no learning). Policy: `agent_v2.py` v2.0, guard = 0.5. Code: Git commit of this file. |

### Cost table (US $)

| Action ↓ / True state → | Normal | Planned | Waste | Compromise |
|---|---|---|---|---|
| Ignore | 0 | 0 | 400 | **5,000** |
| Report | 50 | 50 | 40 | 600 |
| Limit | 300 | **1,500** | 60 | 100 |
| Investigate | +25 added to the next action |

### The decision rule written as thresholds

From the cost table, for any belief:
- **Ignore is cheaper than Report** only if 50·P(N) + 50·P(P) > 360·P(W) + 4,400·P(C).
  In practice, **Report wins as soon as P(Compromise) is above about 1%**.
- **Limit is cheaper than Report** only if 500·P(C) > 250·P(N) + 1,450·P(P) + 20·P(W).
  Here: 500 × 0.096 = 48 < 250 × 0.362 + 1,450 × 0.326 + 20 × 0.217 ≈ 567 → **no Limit**.

---

## Part 2 — How the belief was built (step by step)

**Step A: Prior** (my estimate of how often each cause occurs):
Normal 80%, Planned 8%, Waste 8%, Compromise 4%

**Step B: Evidence "high spike" (6.51×).** Likelihood P(high spike | state):

| | Normal | Planned | Waste | Compromise |
|---|---|---|---|---|
| Prior | 0.80 | 0.08 | 0.08 | 0.04 |
| Likelihood | 0.05 | 0.45 | 0.30 | 0.75 |
| Prior × likelihood | 0.040 | 0.036 | 0.024 | 0.030 |
| **Posterior** (÷ 0.130) | **30.8%** | **27.7%** | **18.5%** | **23.1%** |

**Step C: Evidence "region not new".** Likelihood P(region seen before | state):

| | Normal | Planned | Waste | Compromise |
|---|---|---|---|---|
| Belief | 0.308 | 0.277 | 0.185 | 0.231 |
| Likelihood | 0.85 | 0.85 | 0.85 | 0.30 |
| Product | 0.262 | 0.235 | 0.157 | 0.069 |
| **Posterior** (÷ 0.723) | **36.2%** | **32.6%** | **21.7%** | **9.6%** |

---

## Part 3 — Adding one new item of evidence: the owner tag

**1. Prior probability** (the belief from Part 2): Normal 36.2%, Planned 32.6%, Waste 21.7%, Compromise 9.6%

**2. New evidence:** whether the Lambda function has an owner/team tag.
The mock dataset has **no tag information**, so the true value is unknown. I calculate **both** possible outcomes. This also follows the instruction to look for evidence for the safe state *and* the unsafe state.

**3. Likelihood for each hidden state:**

| | Normal | Planned | Waste | Compromise |
|---|---|---|---|---|
| P(tag **present** \| state) | 0.90 | 0.90 | 0.60 | 0.20 |
| P(tag **missing** \| state) | 0.10 | 0.10 | 0.40 | 0.80 |

Reasoning: a team's own resources are usually tagged. Forgotten resources are often untagged. Attackers rarely tag what they create.

**4. Posterior probability:**

| Outcome | Normal | Planned | Waste | Compromise | P(problem) |
|---|---|---|---|---|---|
| Before the tag | 36.2% | 32.6% | 21.7% | 9.6% | 31.3% |
| **Tag present** (safe evidence) | 42.4% | 38.2% | 17.0% | **2.5%** | 19.5% |
| **Tag missing** (unsafe evidence) | 15.6% | 14.0% | 37.4% | **33.0%** | 70.4% |

Check: each row sums to 100%.

**5. Compare with the decision threshold:**

| Outcome | E[Ignore] | E[Report] | E[Limit] | E[Investigate, then act] | Limit guard (P(C) ≥ 50%)? |
|---|---|---|---|---|---|
| Tag present | $192.5 | **$62.0** | $712.2 | $80.2 | No |
| Tag missing | $1,799.5 | $227.7 | $312.5 | **$144.9** | No |

**6. New action:**

- **Tag present → Report.** Compromise drops to 2.5%. That is still above the ~1% level where Ignore stops being the cheaper choice, so a human takes a quick look. Investigating ($80.2) is not worth it.
- **Tag missing → Investigate**, then act on what CloudTrail and the change log show:

| Launcher known? | Change ticket? | Normal | Planned | Waste | Compromise | Action |
|---|---|---|---|---|---|---|
| Yes | No | 25.6% | 7.7% | 54.7% | 12.1% | **Report** (likely waste) |
| Yes | Yes | 10.1% | 63.6% | 21.5% | 4.8% | **Report** (likely planned) |
| No | No | 4.3% | 1.3% | 20.8% | **73.5%** | **Limit** (passes the 50% guard) |

---

## Part 4 — Comparable historical cases (evidence for the safe state and the unsafe state)

Section 10 asks for recent, comparable historical cases rather than a large dataset that is just easy to find. The most comparable cases are the **other days in the same 30-day billing data**, using the same rule (cost ÷ median of the previous 7 days of the same service).

**Evidence for the safe state (Normal):**
- In the unmodified data, **14 of 115** service-days (**12.2%**) already show a ≥3× spike, with no injected problem. Examples: EC2 on Jul 10 (7.0×), RDS on Jul 11 (8.7×), S3 on Jul 29 (4.7×).
- Lambda itself cost more than $150 on **6 of 30 days** (Jul 7, 10, 16, 17, 19, 26). A $242 Lambda day is unusual, but not unique.
- The usage ratio is only 1.95×. Most of the jump is the price per request, not more requests.

**Evidence for the unsafe state (Waste/Compromise):**
- $242.18 is the single most expensive row in the dataset, and 6.5× the 7-day median.
- The day before, Lambda cost was already $42.60, so the jump is sudden, not a slow rise.

**What this changes in the model:** my likelihood P(high spike | Normal) = 0.05 is **too low** compared with this history (0.122). Recomputing with the historical values (low 0.670, med 0.209, high 0.122):

| | Normal | Planned | Waste | Compromise | Decision |
|---|---|---|---|---|---|
| My estimate (Part 2) | 36.2% | 32.6% | 21.7% | 9.6% | Report ($100.5) |
| Historical P(spike \| Normal) | 58.0% | 21.4% | 14.3% | 6.3% | Report ($83.2) |
| + tag present | 64.2% | 23.7% | 10.5% | 1.6% | Report ($57.5) |
| + tag missing | 31.0% | 11.5% | 30.6% | 27.0% | Investigate ($136.2) |

**The decision does not change** (Report; Investigate if the tag is missing), so it is robust to this correction. The corrected likelihood is a candidate change for the next agent version, and it would probably reduce failure F6 (price-noise false alarms).

**Caution:** this history is mock data, and "unmodified" is only assumed to mean "Normal". In real billing, comparable history should be the same service and account over recent weeks, excluding known incidents.

---

## What would change this decision

- If practitioners say **alert fatigue makes Report much more expensive than $50**, the agent would ignore more of these cases.
- If **stolen keys usually show a known launcher** (failure F3), the "launcher known" row above underestimates compromise.
- The prior (4% compromise) and all likelihoods are **my estimates, not measured from historical incidents**. No labeled dataset of real AWS cost incidents was used to estimate them; finding one, or getting estimates from practitioners, is a next step. This is the main limitation of this record.
