# AI Review Record

Three different reviews (Section 11). Each comment was checked before it was accepted or rejected.

**Independence note:** Reviews 1–3 were done with Claude, which also helped write the code. A reviewer that helped build the work may miss its own blind spots. Review 4 should be run in **Gemini** (the course's suggested tool) with the prompt at the end of this file, and its comments added to this table.

## Review 1 — Practitioner review (Claude)

Prompt: *"Act as an experienced FinOps/SRE engineer. Review this cloud cost agent (problem, agent.py, agent_v2.py, failure-analysis.md). Find unrealistic assumptions, missing users or stakeholders, deployment risks, actions that can cause harm, and actions that cause unnecessary work."*

| AI tool | Review comment | Accept or reject | Reason | Change | Evidence |
|---|---|---|---|---|---|
| Claude | **P1** Daily billing data is too slow. A compromise can cost thousands within hours, before a daily row exists. | Accept | Real AWS billing data can lag by hours; my test cannot show this. | Added as a limitation in the paper. No code change (no hourly data). | Paper §10 |
| Claude | **P2** Missing stakeholders: the FinOps/finance team (owns the budget), the security team (owns compromise response), and service owners (whose workloads get limited). | Accept | The cost of each error falls on different people (§12 answers). | Stakeholders named in the paper and in the §12 answers. | `research-file.md` §13, paper §5 |
| Claude | **P3** Auto-Limit is dangerous: F7 shows a planned job was shut down. In production, every Limit should need human approval. | Accept (partly) | Agree for deployment. For the experiment, I keep the 50% guard so the trade-off stays measurable. | Paper states that deployment requires human approval for every Limit. | `failure-analysis.md` F7, ablation |
| Claude | **P4** A Report is not $50. A 57% human-review rate would cause alert fatigue, and engineers would start ignoring reports. | Accept | This is the most important unchecked assumption in the cost table. | **New test:** `experiments/run_sensitivity.py`. With Report = $150, v2 false alarms drop from 14.2 to 3.2 and v2 is still the cheapest policy. | `results/sensitivity.md` |
| Claude | **P5** Compare with AWS Cost Anomaly Detection, the real product, not just a z-score rule. | Reject | AWS Cost Anomaly Detection runs only on a real AWS account; it cannot run on this mock CSV. A z-score rule is a fair stand-in for a threshold alert. | Mentioned in related work as future work. | — |
| Claude | **P6** "Owner tag is free" assumes the company has a tagging policy. Many teams don't tag, so missing tags are common and not suspicious. | Accept | This is exactly failure F7. | Added as a limitation; added as a Reddit question. | `failure-analysis.md` F7 |
| Claude | **P7** Add more actions, such as "snapshot then stop" or "rotate the access key". | Reject (for now) | Good ideas, but they add actions with costs I cannot yet estimate. The project asks for the smallest testable agent. | Listed as future work. | — |

## Review 2 — Probability review (Claude)

Prompt: *"Act as a statistician. Check the hidden states, prior probabilities, likelihood estimates, decision thresholds, error costs, calibration, and evidence for alternative explanations in this agent and its probability decision record."*

| AI tool | Review comment | Accept or reject | Reason | Change | Evidence |
|---|---|---|---|---|---|
| Claude | **Q1** The prior (4% compromise) is not based on any data. | Accept | True; there is no labeled incident data. | **New test:** prior varied from 1% to 10% in `run_sensitivity.py`. v2 is cheapest in all cases. | `results/sensitivity.md` |
| Claude | **Q2** Naive Bayes assumes clues are independent, but "owner tag missing" and "unknown launcher" are probably linked. This double-counts evidence. | Accept | Correct; this may make the agent overconfident about compromise (a possible cause of F7). | Added as a limitation. No code change: a joint model needs more data than 40 cases. | Paper §10 |
| Claude | **Q3** The cases were generated with likelihoods close to the agent's own. The test partly checks the agent against its own assumptions, so results are optimistic. | Accept | This is the biggest weakness of the experiment. | Stated clearly in the paper's abstract and limitations. | `src/make_cases.py` vs `src/agent.py` |
| Claude | **Q4** One Brier score is not enough to judge calibration. | Accept | A calibration table shows *where* the beliefs are wrong. | **New test:** `experiments/run_calibration.py`. Both versions are under-confident (e.g. predicted 4%, observed 16%). ECE: v1 0.163 → v2 0.126. | `results/calibration.md` |
| Claude | **Q5** The test mix is 40% problems, but the prior says 12%. This explains the under-confidence, and the dollar totals do not reflect real-world frequency. | Accept | Correct, and it explains the Q4 result. | Explained in the paper. | `results/calibration.md` |
| Claude | **Q6** Alternative explanations are missing: an AWS price change, an expired discount (Savings Plan), or delayed billing data. | Accept | F6 (price-noise false alarm) may really be this. | Added as future hidden states in the paper. | `failure-analysis.md` F6 |
| Claude | **Q7** The learning step should also learn the prior from feedback. | Reject | The test mix (40% problems) is not the real base rate; learning it would make the agent fit my test design, not reality. | No change. | — |

## Review 3 — Preprint review (Claude)

Prompt: *"Act as a strict conference reviewer. Review paper/main.tex for: clear problem statement, new information, correct methods, test design, baseline quality, repeatable results, limitations, ethics, claims without evidence, and questions for the next version."*

| AI tool | Review comment | Accept or reject | Reason | Change | Evidence |
|---|---|---|---|---|---|
| Claude | **R1** The "User discussions" section is empty. The course requires information from human discussions. | Accept | Correct; the paper cannot be final without it. | Red TODO left in the paper; fill it after Reddit/X. | `paper/main.tex` §2 |
| Claude | **R2** The title says "agent", but no action touches a real AWS account. Readers may think it was deployed. | Accept | Accuracy matters. | Added: actions are selected and logged, not executed. | Paper §3 |
| Claude | **R3** The baseline is unfair: v2 uses usage data, but the baseline sees only cost. | Accept | A fair comparison must give both the same information. | **New baseline** `policy_baseline_usage` (z-score on cost or usage). Its cost falls to $12,214, but v2 ($4,038) is still about 3× cheaper. | `results/seeds_metrics.md`, Table 2 |
| Claude | **R4** "Cheaper in 25 of 30 sets" has no significance test. | Accept | Easy to add and makes the claim checkable. | Added a two-sided sign test: p = 0.0003. | `experiments/run_seeds.py` |
| Claude | **R5** The conclusion ("far cheaper decisions") overclaims, given that the test shares the agent's assumptions. | Accept | Agree with limitation Q3. | Conclusion rewritten: shows the decision rule is consistent, not that it works on real incidents. | Paper §9 |
| Claude | **R6** Dollar figures such as $4,038 suggest false precision, since the costs are guesses. | Reject | The numbers are exact, repeatable outputs of the stated cost table, and the paper already labels the table as estimates and tests sensitivity. | No change. | Table 1, sensitivity paragraph |
| Claude | **R7** No evidence that compromises really cost about $5,000 or that cryptojacking via leaked keys is common. | Accept (as a gap) | I have not read a source I can cite for this, and the rules forbid citing unread sources. | Kept as an open question and a Reddit question; sensitivity covers $2,000–$20,000. | `results/sensitivity.md` |

## Review 4 — Independent review (Gemini) — to do

Paste this into Gemini with `paper/preprint-draft.pdf` attached, then add each comment to this table (decide accept/reject yourself, with a reason):

| AI tool | Review comment | Accept or reject | Reason | Change | Evidence |
|---|---|---|---|---|---|
| Gemini | | | | | |

```text
You are a strict reviewer for an AI conference. Review this student preprint.
Check: clear problem statement, new information, correct methods, test design,
baseline quality, repeatable results, limitations, ethics, claims without evidence,
and questions for the next version. For each problem, quote the exact sentence
or table, explain why it is a problem, and suggest a fix. Do not praise.
```
