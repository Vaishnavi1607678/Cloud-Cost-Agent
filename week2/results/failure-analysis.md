# Week 2 Failure Analysis

Source: every wrong decision of **P3** (before the design changes) on the main 500 cases (seed 42), in `results/failures_raw.md`. P3 made 146 wrong decisions: 113 Normal→Report, 15 Planned→Report, 6 Other→Ignore, 4 Waste→Ignore, 3 Compromise→Report, 2 Other→Report, 1 Normal→Limit, 1 Waste→Report, 1 Waste→Limit.

"Extra cost" = cost of P3's decision minus the cost of the best action for the true state.
All probabilities and costs are hypothetical (see `src/model.py`).

## Summary

| ID | Name | Case | Truth → action | Extra cost | Category | Fixed? |
|---|---|---|---|---|---|---|
| FW2-1 | Forgotten planned job | S0126 | Waste → Ignore | $3,362 | Wrong cost assumption (+ misleading evidence) | **Yes, DC1** |
| FW2-2 | Price change ignored | S0378, S0141 | Other → Ignore | $216, $199 | Wrong cost assumption | **Yes, DC1** |
| FW2-3 | Untagged normal work looks like an attack | S0081 | Normal → Limit | $301 | Misleading evidence (dependent clues) | **Yes, DC3** |
| FW2-4 | Stolen keys look like a known user | S0116 | Compromise → Report | $502 | Misleading evidence | No (open question) |
| FW2-5 | Quiet compromise | S0480, S0023 | Compromise → Report | $500, $502 | Insufficient information | No (acceptable) |
| FW2-6 | Slow leak | S0214 | Waste → Ignore | $519 | Bad evidence (signal not available) | No (needs new evidence) |
| FW2-7 | Insurance reporting | 113 cases | Normal → Report | $50 each | Wrong cost assumption | Partly (tested in Week 1 sensitivity) |
| FW2-8 | Missing residual state | ablation | Other forced into 4 states | +$452 per 500 | Missing hidden state | **Yes, DC2** |

---

## FW2-1 Forgotten planned job (S0126) — the most expensive failure

Waste, **$509/day**. P3 chose **Ignore**. Extra cost **$3,362**.

1. **What did the agent believe?** Planned 0.726, Normal 0.237, Waste 0.031, Compromise 0.001, Other 0.006.
2. **What was true?** Waste.
3. **Evidence used:** high spike, no price jump, region seen, tagged; then bought ticket (**found**) and launcher (**known**).
4. **Evidence never obtained:** ask_owner (would have said **not intended**), forensics (clean).
5. **Was the probability wrong?** Given my likelihoods, no. A change ticket really is strong evidence for Planned. But the ticket was for a job that ran and then was **never shut down**, so the evidence was true and pointed the wrong way.
6. **Was the hidden-state list incomplete?** Partly. "A planned job that turned into waste" is a mix of two states my list treats as separate.
7. **Was the threshold wrong?** Yes, because of the cost below. The agent assumed every bill is $60/day, so ignoring waste "cost" $400. At $509/day it really costs 6.67 × $509 = $3,395.
8. **Was the cost model wrong?** Yes. This is the main cause.
9. **Should it have asked for more?** Yes. With the real stakes, asking the owner ($40) is clearly worth it.
10. **Should a human have been involved?** Yes. A $509/day line item that is 3× its median should reach a person.

**Category:** Wrong cost assumption (primary), Misleading evidence (secondary).
**Design change DC1:** the cost of ignoring a problem now depends on the actual bill (`scaled_costs=True`, policy P3b). The Ignore/Report break-even falls from 1.1% at $60/day to 0.15% at $1,000/day (`results/analysis.md` §5).
**Re-test:** P3b chooses **Report** for S0126. Over 20 seeds × 500 cases, total cost fell from **$18,152 to $16,409** (−9.6%), lower in **18 of 20** seeds, and P3b bought fewer checks (0.52 → 0.28 per case). Price paid: recall fell from 0.897 to 0.849, because small waste cases now look cheaper to ignore.

## FW2-2 Price change ignored (S0378, S0141)

Other (a price change), $147/day and $138/day. P3 chose **Ignore**.

1. Belief: Normal ≈ 0.80, **Other ≈ 0.17**. 2. Truth: Other. 3. Used: price_jump = **yes**, low spike. 4. Not needed. 5. Probability was reasonable: the residual state did its job and raised Other from 4% to 17%. 6. List complete (thanks to DC2). 7–8. **Cost wrong:** at $60/day ignoring a price change costs $100, so 17% × $100 < $50 for a Report. At the real $147/day it costs $245. 9. No. 10. A finance person, yes.

**Category:** Wrong cost assumption. **Fixed by DC1:** P3b reports both cases.

## FW2-3 Untagged normal work looks like an attack (S0081)

Normal, $44/day. P3 chose **Limit** and stopped a normal workload.

1. **Belief:** Compromise **0.658**, Normal 0.261. 2. **Truth:** Normal. 3. **Used:** low spike, **new region**, **untagged**, launcher **unknown**. 4. **Never obtained:** ticket (none), ask_owner (would say not intended, so it would not have helped), forensics (**clean**). 5. **Probability wrong?** Yes. Naive Bayes multiplies "untagged" and "unknown launcher" as if they were independent, but automation roles create untagged resources and appear unknown in CloudTrail, so the two clues come together. The evidence is counted twice. 6. List complete. 7. **Threshold:** the 0.5 guard let a 66% belief trigger an automatic Limit. 8. Costs fine. 9. Forensics would have cleared it, but costs $2,000 + 48h. 10. **Yes, a human should approve this Limit.**

**Category:** Misleading evidence (dependent clues treated as independent).
**Re-test of the cause:** in the misspecified simulator, where this dependence is real, P3b's wrong Limits rise from **1.15 to 5.85** per 500 cases, and P3 becomes **more expensive than P2** ($23,236 vs $19,433). Buying the launcher check made things worse. This is a real case of "more information made the decision worse" (Advanced Q3).
**Design change DC3:** automatic Limit needs P(Compromise) ≥ **0.7** (policy P3c).
**Re-test:** S0081 → **Report**. Misspecified world: wrong Limits 5.85 → **3.80**, cost $19,655 → **$19,278**. Matched world: cost +$239 ($16,409 → $16,648). A 0.9 guard nearly removes wrong Limits (0.30) but costs ~$2,200 more, because real compromises then go to a human ($600) instead of being limited ($100) (`results/guard.md`). I chose 0.7 because it has the **lowest worst case** across the two worlds.

## FW2-4 Stolen keys look like a known user (S0116)

Compromise, $65/day. P3 chose **Report** (best: Limit).

1. Belief: Normal 0.357, Waste 0.340, Planned 0.217, **Compromise 0.081**. 2. Truth: Compromise. 3. Used: high spike, untagged, then launcher = **known**. 4. Never obtained: ask_owner (would say **intended**, also misleading!), forensics (**malicious**). 5. Probability: likely wrong. With stolen keys, CloudTrail shows the real user, and the owner may think it was their own job. My P(known | Compromise) = 0.30 is a guess. 6. List complete. 7. Threshold fine. 8. Costs fine. 9. Only forensics would have helped, and it is not worth $2,000 + 48h at this belief. 10. Report already sends it to a human, so the damage is limited ($600 instead of $100).

**Category:** Misleading evidence. **Not fixed.** Changing the likelihood without real data would just tune the model to my own simulator. This is a question for practitioners (`discussion-record.md`).

## FW2-5 Quiet compromise (S0480, S0023)

Compromise with a **medium** or **low** spike. P3 chose **Report**.

1. Belief: P(Compromise) only **0.042** and 0.045. 2. Truth: Compromise. 3. Used: free evidence (S0480 bought nothing; S0023 bought launcher = unknown). 4. Never obtained: ask_owner (**not intended**), forensics (**malicious**). 5. Probability low but honest: little evidence pointed to compromise. 6. Complete. 7–8. Fine. 9. Asking the owner would have raised P(Compromise) sharply, but its value of information was negative: Report was already the action, and no answer would have changed it to Limit at that belief. 10. Report = a human is involved.

**Category:** Insufficient information. **Not changed:** Report is the right *safe default* here, and the extra cost is $500. This is the case where "the information would help, but it cannot change the action, so it is not worth buying."

## FW2-6 Slow leak (S0214)

Waste, $84/day, **low spike**. P3 chose **Ignore**.

1. Belief: Normal 0.968, Waste 0.013. 2. Truth: Waste. 3. Used: low spike, tagged, seen region. 4. Never obtained: ask_owner (not intended). 5. Probability: correct given the evidence. Nothing looked wrong. 6. Complete. 7–8. Fine. 9. No affordable check was justified. 10. No.

**Category:** Bad evidence (the right signal is not available). A slow leak doesn't spike. **Not fixed.** It needs a new evidence source, such as resource utilisation (an idle instance is waste whatever its cost). New question in the paper.

## FW2-7 Insurance reporting (113 Normal → Report)

The most common error. With a 1.1% break-even, any case with even a small chance of compromise is reported. Each costs only $50 here, but 113 of them is real human load. **Category:** Wrong cost assumption (a Report's real cost includes alert fatigue). Tested in Week 1's sensitivity analysis: with Report = $150, false alarms dropped from 14.2 to 3.2 per 40 cases.

## FW2-8 Missing residual state (ablation)

Run P3b with only the Week 1 states (no "Other"), on worlds that contain price changes. Over 20 seeds: total cost **$16,861 vs $16,409** with Other (with-Other cheaper in **15 of 20** seeds), and **cross-entropy 1.473 vs 0.778 bits**. Without Other, the agent gives probability 0 to something that happens, so its log loss on those cases is huge. KL(world ∥ agent) is infinite. **Category:** Missing hidden state. **DC2:** keep the residual state.

---

## What changed and what was re-measured

| Change | From failure | Re-test (20 seeds × 500 cases) |
|---|---|---|
| DC1 costs depend on bill size | FW2-1, FW2-2 | $18,152 → $16,409; better in 18/20 seeds |
| DC2 residual "Other" state | FW2-8 (Week 1 F6) | $16,861 → $16,409; cross-entropy 1.47 → 0.78 bits |
| DC3 Limit guard 0.5 → 0.7 | FW2-3 | Misspecified: wrong Limits 5.85 → 3.80, cost $19,655 → $19,278; matched: +$239 |

## Not hidden: where my agent did not win

- In the **misspecified** world, the final policy P3c beats the simple threshold policy P2 in only **12 of 20** seeds ($19,278 vs $19,433). Most of the advantage disappears when the agent's model of the evidence is wrong. In the matched world it wins 19 of 20.
- P1 (most likely state) has the **highest accuracy** (0.871) of all policies and costs **4.4×** more than P3c. Accuracy is the wrong headline.
