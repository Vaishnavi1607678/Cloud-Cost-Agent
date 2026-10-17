# Study Guide — understand and defend your Week 1 + Week 2 project

The course grades whether **you** can reason about this, not whether the files exist. Read this once, then try to answer each question below **out loud without looking**. If you can't, re-read that part. About 2–3 hours total.

---

## Part 1 — The whole project in 6 sentences

1. When an AWS bill jumps, the agent can't see **why**: normal, planned job, waste, hack (compromise), or something else (like a price change).
2. So it keeps a **belief**: a probability for each cause, adding to 100%.
3. Each clue (spike size, new region, owner tag, CloudTrail, ticket…) **updates** the belief with Bayes' rule.
4. Each action (ignore / report to a human / limit) has a **cost** if it's wrong, so the agent picks the action with the **lowest expected cost**, not the most likely cause.
5. Some clues cost money and time, so before buying one it asks: **"Could any answer change what I'd do, and is that worth the price?"** (value of information).
6. Tested on 500 simulated cases × 20 seeds, the cost-aware agent beats simple rules on cost. But it raises more alarms, and when its assumptions are wrong its advantage mostly disappears.

---

## Part 2 — Every idea, with your numbers

**Bayes' rule (one example).** Prior chance of compromise = 3%. 75% of compromises cause a high spike; only 12% of normal days do. After seeing a high spike, compromise goes from 3% to **12.4%**.
*How:* multiply each prior by "how likely is a high spike if this were the cause", add them up (0.1811), divide each by that total.

**Likelihood vs probability.** "75% of hacks cause high spikes" (likelihood) is NOT "75% of high spikes are hacks". The real answer is 12.4%. Confusing these is the #1 mistake.

**Entropy = confusion in bits.** 0 bits = certain. With 5 causes, maximum = 2.32 bits. The prior is 1.18 bits.
*Surprise:* after a high spike, entropy goes **up** to 1.89. The agent knows more, but it moved from "probably normal" to "something's happening, but I don't know what."

**Information gain = expected drop in confusion.** CloudTrail: 0.24 bits. Forensics: 0.63 bits. Information gain is the same thing as **mutual information**.

**Value of information = money, not bits.** CloudTrail ($1): **+$55**. Forensics ($2,000 + 48 hours): **−$2,414**. Rule: *only buy a check if some answer could change your action, and the saving beats the price.* In 600 situations, the most informative check was the best buy only 2 times.

**Threshold from costs.** False alarm $50, missed hack $5,000 (vs $600 if reported). Break-even = 50 / (50 + 4,400) = **1.1%**. Same maths as the umbrella: carry cost ÷ (carry cost + getting-wet cost). Bigger bill → lower threshold (0.15% at $1,000/day).

**Why three actions?** With only ignore/limit, a 1% threshold would shut down almost everything. "Report to a human" is the cheap middle action that makes a low threshold usable.

**KL divergence.** How badly one belief describes another world. Not symmetric: KL(posterior‖prior) = 1.05 bits but KL(prior‖posterior) = 0.90 bits. If the agent gives 0% to something that happens (no "Other" state), KL is **infinite**.

**Jensen–Shannon divergence.** A symmetric, always-finite version of KL. Used as an **alarm**: compare this month's free evidence to the old pattern. With 500 cases per window, it caught the startup→enterprise change 98% of the time; with 100 cases, only 11%.

**Calibration.** When the agent says 30%, is it right 30% of the time? Expected calibration error 0.018 (good). It gets worse (0.024) when the agent's assumptions are wrong.

**Cross-entropy (log loss).** Average surprise at the truth. With the "Other" state: 0.78 bits. Without it: 1.47 bits, because the agent is infinitely surprised by price changes.

**Distribution shift.** The world changes, the agent doesn't. Startup model in an enterprise world: $21,578 vs $19,725 if re-fitted.

**Your two "beyond the brief" concepts:**
- **Selection bias in feedback.** The agent only hears about problems it flagged. Ignored problems are silently counted as "fine", so it learns the world is safer than it is (waste stuck at 10% vs the true 12%). Fix: audit a random 5% of ignored cases and count each one ×20 (**inverse-probability weighting**) → 11.7%.
- **Conditional independence.** Naive Bayes multiplies clues as if each were new information. "No tag" and "unknown launcher" both come from the same automation role, so multiplying counts one fact twice. In that world, buying more evidence made the agent **worse** (5.8 wrong shutdowns vs 1.2).

---

## Part 3 — The experiment in one table (20 seeds × 500 cases)

| Policy | What it does | Accuracy | Total cost |
|---|---|---|---|
| P0 | always ignore | 0.86 | $235,240 |
| P1 | most likely cause | **0.87** (best) | $72,704 |
| P2 | lowest expected cost, free clues only | 0.59 | $19,313 |
| P3 | + buys checks by value of information | 0.69 | $18,152 |
| P3b | + cost depends on bill size | 0.67 | **$16,409** |
| P3c | + needs 70% sure before shutting down | 0.67 | $16,648 |

**Key message:** the most accurate policy costs 4× more. Accuracy is the wrong headline when mistakes have different prices.

## Part 4 — The three design changes (and why)

1. **Cost depends on bill size** — a $509/day waste was ignored because the agent assumed every bill is $60. Fixed it; cost down ~10%.
2. **Residual "Other" state** — without it, price changes break the agent (log loss doubles).
3. **Guard 0.5 → 0.7** — an untagged normal workload got shut down. Fewer wrong shutdowns when assumptions are wrong; costs slightly more when they're right. I chose the safer worst case.

## Part 5 — Honest limitations (say these before anyone asks)

- Everything is **simulated**. The cases come from my own likelihood tables, so the test checks the **policy**, not whether the likelihoods are true.
- Almost all probabilities and costs are **my assumptions**. Only the normal-day spike rate and the $60 typical bill come from the data, and that data is mock.
- When my assumptions are wrong (misspecified world), my best agent beats the simple threshold policy in only 12 of 20 runs.
- No human discussions have changed the model yet.

---

## Part 6 — Practice questions (answer out loud)

1. What is your hidden state, and why can't the agent just ask an LLM "is this a hack?"
2. Walk me through one Bayes update with your numbers.
3. Why did entropy go UP after you saw a high spike? Isn't evidence supposed to reduce uncertainty?
4. Why is your threshold 1.1% and not 80%?
5. Your forensics check is the most informative. Why doesn't the agent use it?
6. Give one case where the most informative question IS the right one.
7. Why is KL divergence not a distance? Give your example.
8. Why use JSD for the alarm instead of KL?
9. Your most accurate policy is P1. Why don't you recommend it?
10. What happens if the cost of a missed hack is 100× higher? (Answer: the human-review rate goes to ~96–99%, and human capacity becomes the real limit.)
11. What happens if checks cost 10× more? (Questions per case: 0.28 → 0.12; the agent still beats P2.)
12. How would your agent notice the world changed, before any labels arrive?
13. Why does learning from feedback go wrong, and how did you fix it?
14. When did adding information make your agent worse? Why?
15. Which of your numbers would you trust least, and how would you get a better one?

---

## Part 7 — What you still need to do yourself

- [ ] Read this guide and answer the 15 practice questions out loud
- [ ] Re-write the concept explanations in `research-file.md` §4 in your own words
- [ ] Rewrite the 20 appendix answers in the paper in your own words (the brief requires your own words)
- [ ] Reddit/X discussions; fill in `discussion-record.md`
- [ ] Read any reference before citing it
- [ ] Compile the paper with the official IJCAI kit → `paper/preprint.pdf`
- [ ] Post the 5 LinkedIn posts (spread out) and the X thread
