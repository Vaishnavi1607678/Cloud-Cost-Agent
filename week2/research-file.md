# Week 2 Research File

## 1. Same problem as Week 1

> The agent observes a daily AWS cost line item (service, region, usage, cost) and that service's recent history. It must choose to ignore, investigate, limit, or report the cost because the cause of the cost change is not known.

## 2. Narrowed research question (brief Section 6)

> **When an AWS cost line item spikes, which check should the agent run next (owner tag, CloudTrail launcher, change ticket, asking the owner, or a security investigation), and at what belief should it stop checking and ignore, report, or limit the cost?**

## 3. What changed from Week 1

| Week 1 | Week 2 |
|---|---|
| 4 hidden states | 5, with a residual **Other** state (price change, expired discount, billing correction, anything else) |
| One "Investigate" action that bought 3 clues together for $25 | 4 separate paid checks with their own price and delay; the agent chooses which to buy, one at a time |
| Value of information only for the bundle | Entropy, information gain per check, value of information, stop rule |
| Fixed costs | Costs of ignoring a problem depend on the bill size (from failure FW2-1) |
| 40 cases | 500 cases per run, 20 seeds, matched and misspecified simulators |
| No shift detection | Jensen–Shannon divergence alarm on the free evidence |
| Learning assumed full feedback | Asymmetric feedback simulated, plus an audit fix |

## 4. Concepts, in my own words, with a number from my problem

The explanations below are **drafts written with AI assistance** (Claude), checked against the numbers produced by `src/model.py`.
**To do (me):** for each concept, paste the brief's Section 7 prompt with my problem, then close the chat and rewrite the explanation in my own words from memory. Tick when done: ☐

| Concept | My explanation | Number from my problem |
|---|---|---|
| Belief | A probability for every possible cause, adding to 1. | Prior: Normal 0.78, Planned 0.08, Waste 0.07, Compromise 0.03, Other 0.04 |
| Bayes update | New belief = old belief × how likely the evidence is under each cause, then rescale to sum to 1. | High spike: Compromise 0.03 → 0.124 |
| Likelihood vs probability | P(evidence given cause) is not P(cause given evidence). 75% of compromises spike high, but only 12.4% of high spikes are compromises. | 0.75 vs 0.124 |
| Entropy | How confused the agent is, in bits (yes/no questions). 0 = certain; 2.32 = all 5 causes equally likely. | Prior 1.177 bits |
| Information gain | How much a check is expected to reduce entropy, averaged over its possible answers. | Launcher: 0.244 bits |
| Conditional entropy | The confusion expected to remain after seeing a signal. | H(S given spike) = 1.006 bits |
| Mutual information | The same number as information gain: how much a signal and the hidden cause tell you about each other. Unlike correlation, it works for categories and any shape of relation. | I(S; spike) = 0.171 bits |
| Cross-entropy (log loss) | How surprised the agent is, on average, by the true cause. Lower is better. Punishes confident wrong beliefs heavily. | P3c: 0.778 bits; without the residual state: 1.473 bits |
| KL divergence | How badly belief Q describes a world that really follows P. Not symmetric, so not a distance. | KL(post ∥ prior) = 1.047, KL(prior ∥ post) = 0.898 bits. Infinite if the agent gives 0 to something that happens (no Other state) |
| Jensen–Shannon divergence | A symmetric, always-finite version of KL (compare both to their average). Good for alarms. | Startup vs enterprise free-evidence patterns: 0.0230 vs 0.0094 bits (500-case windows) |
| Calibration | When the agent says 30%, it should be right about 30% of the time. | ECE 0.018 (matched) → 0.024 (misspecified) |
| Expected cost | Average cost of an action over all possible causes, weighted by belief. | Report $162.8 vs Ignore $1,179.9 in the decision record |
| Value of information | How much cheaper the decision is expected to be after a check, minus the check's price and delay. Zero if no answer can change the action. | Launcher +$55; forensics −$2,414 |
| Exploration vs exploitation | Sometimes pay to learn (explore) even when you could act now. My audit of 5% of ignored cases is exploration. | Audit cut KL(world ∥ learned prior) from 0.0154 to 0.0025 |
| Distribution shift | The world the agent works in changes, but its priors and likelihoods don't. | Startup → enterprise: cost $19,725 (re-fitted) vs $21,578 (stale) |

## 5. Extension rule: two concepts I found from my own results

### Concept 1 — Selection bias in feedback (and inverse-probability weighting)
- **How it was found:** the brief warned that feedback is asymmetric. In `run_feedback.py` the learning agent counted every ignored case as Normal. Its estimate of waste got stuck at 0.10 when the truth was 0.12, and more data did not fix it. The question "why doesn't more data fix it?" leads to **selection bias** (labels are missing *because of* the agent's own decision), and its standard fix, **inverse-probability weighting**. (Found while building with AI assistance; to verify by reading one source on selection bias before citing.)
- **Plain words:** if you only hear back about the cases you flagged, your data is not a fair sample of the world. Audit a random share of the cases you ignored and count each audited case as standing for all the ones you didn't audit (weight 1/0.05 = 20).
- **Number:** learned P(Waste) after 5,000 cases: full feedback 0.120, asymmetric 0.100, **audit 5% with weights 0.117**.
- **When it would be a mistake:** if the audit is not random (for example, only auditing big bills), the weights are wrong and the bias comes back.

### Concept 2 — Conditional independence (naive Bayes double counting)
- **How it was found:** failure FW2-3, where an untagged normal workload was limited, and the misspecified simulator, where buying the CloudTrail check made P3 *worse* than not buying it ($23,236 vs $19,433). The question "why does adding a true signal make decisions worse?" leads to **conditional independence**. (Found while building with AI assistance.)
- **Plain words:** multiplying likelihoods assumes each clue brings new information once the cause is known. "No tag" and "unknown launcher" both come from the same automation role, so multiplying them counts one fact twice and makes the agent overconfident.
- **Number:** misspecified world, wrong Limits per 500 cases: 1.15 (matched) → **5.85**; guard 0.7 reduces it to 3.80.
- **When it would be a mistake to worry about it:** if the clues really are independent given the cause, as in my matched simulator, naive Bayes is fine.

## 6. Reading (optional this week)

I have not yet read research papers for Week 2. The Week 1 references are in `week1/.../paper/references.bib`. From the Week 1 list, **Howard (1966), Information Value Theory**, is the one most connected to this week (value of information). If I read it, I will answer the brief's 7 questions before citing it. I will not cite anything I have not opened.

## 7. AI prompts used this week

| Purpose | Prompt (short) | What I had to check or fix |
|---|---|---|
| Concepts | The brief's Section 7 prompts and the general "Explain [CONCEPT] to me as if I have never studied ML…" prompt, with my problem pasted in | Checked every number against `src/model.py` output |
| Code | Build the model, simulator, policies, experiments | Found and fixed: (1) a cost model that multiplied the whole $5,000 by the bill size (unrealistic $100k losses); (2) an audit fix that still counted un-audited cases as Normal |
| Review | Ask an AI to find what's unrealistic in the enterprise scenario and the cost model | (to do: record in `discussion-record.md` / paper) |

## 8. Questions to ask humans this week (Reddit / X)

1. With stolen AWS keys, how often does CloudTrail show a real, known user? (FW2-4)
2. Would you allow an automatic stop when the resource is untagged and the launcher is an unknown role? (FW2-3)
3. What is the real cost of one unneeded cost alert in your team? (FW2-7)
4. How long does wasted spend usually run before someone notices: days or weeks? (cost model: 6.7 days)
5. Do you audit a sample of the alerts you *didn't* raise? (feedback bias)
6. Which signal catches a slow leak that never spikes? (FW2-6)
