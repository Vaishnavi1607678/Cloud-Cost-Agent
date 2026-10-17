# Week 2 — A Probabilistic View of the Cloud Cost Agent

Same problem as Week 1:

> The agent observes a daily AWS cost line item and its 7-day history. It must ignore, report, or limit the cost, because the cause of the change is not known.

**Week 2 question:** *When an AWS cost line item spikes, which check should the agent run next, and at what belief should it stop checking and act?*

New in Week 2: a residual hidden state, four paid checks with prices and delays, entropy and information gain, value of information, a stop rule, costs that depend on the bill size, a Jensen–Shannon shift alarm, and a study of one-sided feedback.

## Main results (20 seeds × 500 simulated cases, mean)

| Policy | Accuracy | Total cost | Checks/case | Human review |
|---|---|---|---|---|
| P0 always ignore | 0.861 | $235,240 | 0 | 0% |
| P1 most likely cause | **0.871** | $72,704 | 0 | 10% |
| P2 expected-cost threshold | 0.590 | $19,313 | 0 | 49% |
| P3 + value of information | 0.685 | $18,152 | 0.52 | 38% |
| P3b + stakes-dependent costs | 0.673 | **$16,409** | 0.28 | 38% |
| P3c + Limit guard 0.7 (final) | 0.672 | $16,648 | 0.28 | 38% |

- The most accurate policy (P1) costs **4.4×** more than the final policy.
- The most informative check (forensics, 0.63 bits) has a value of **−$2,414**; the $1 CloudTrail check has **+$55**. The most informative check was the best buy in only **2 of 600** situations.
- When the agent's assumptions are wrong (misspecified simulator), the final policy beats the simple threshold policy in only **12 of 20** seeds.
- With one-sided feedback, the learned waste rate gets stuck at 10% (truth 12%). A weighted 5% audit brings it to 11.7%.

All probabilities and costs are **hypothetical** unless marked *measured* in `src/model.py`.

## Run it

Python 3.9+ and `matplotlib`.

```bash
cd week2/experiments
python3 run_main.py            # main table: 500 cases, seed 42
python3 run_analysis.py        # belief table, evidence comparison, 5 questions, thresholds, KL/JSD, umbrella
python3 run_robustness.py      # 20 seeds, matched + misspecified simulator, design-change re-tests
python3 run_guard.py           # DC3: Limit guard 0.5 / 0.7 / 0.9
python3 run_generalization.py  # cost x100, checks x10, startup -> enterprise, JSD alarm
python3 run_feedback.py        # one-sided feedback and the audit fix
python3 run_failures.py        # wrong decisions, before/after the design changes
python3 make_figures.py        # paper figures
```

All seeds are fixed, and every policy runs on identical cases. Labels are only read after all decisions are made.

## Files

| Path | What it is |
|---|---|
| `src/model.py` | States, priors (with origin), 8 evidence sources, costs, entropy / information gain / KL / JSD / value of information |
| `src/simulate.py` | Matched and misspecified simulators; bill amounts drawn from the Week 1 data |
| `src/policies.py` | P0–P3, P3b, P3c, stop rule, human-control guard |
| `src/evaluate.py` | True cost, accuracy, precision, recall, human review, calibration (ECE), cross-entropy |
| `results/` | All tables (`*.md`), raw numbers (`*.json`), predictions (`*.csv`), `failure-analysis.md` |
| `decisions/decision-record.md` | One case worked step by step |
| `research-file.md` | Narrowed question, concepts with my numbers, two concepts beyond the brief |
| `discussion-record.md` | Continued from Week 1 |
| `social/` | 5 LinkedIn drafts, X thread |
| `paper/` | LaTeX source, figures, draft PDF |
| `STUDY-GUIDE.md` | Plain-English guide + practice questions to defend the work |

## Submission checklist (brief Appendix D)

| Item | Status |
|---|---|
| Same problem as Week 1 | ✅ |
| Hidden states incl. residual state | ✅ Other |
| Priors with origin | ✅ `decisions/decision-record.md` §1 |
| One full Bayes update by hand | ✅ |
| Entropy before and after | ✅ |
| ≥3 evidence sources compared on value and cost | ✅ 4 paid + 4 free |
| Five candidate questions tabled | ✅ `results/analysis.md` §3 |
| Threshold derived from costs | ✅ 1.1%, moves with bill size |
| Expected-cost calculation | ✅ |
| Human escalation rules | ✅ guard 0.7, $3,000/day ceiling, uncertain band → Report |
| Stop condition | ✅ |
| Two concepts beyond the brief | ✅ selection bias in feedback; conditional independence |
| KL, JSD, mutual information, conditional entropy, calibration, value of information | ✅ |
| Umbrella problem with my own costs | ✅ |
| Generalization: all three variable changes | ✅ |
| ≥100 cases, baseline, ≥2 policies, seed reported, identical cases | ✅ 500 × 20 seeds |
| ≥1 table and ≥1 figure | ✅ |
| ≥5 failures analysed and classified | ✅ 8 |
| Design change made because of a failure, and re-tested | ✅ 3 (DC1–DC3) |
| Paper: specific title, hypothetical labels, limitations, new questions, 20 questions, AI-use statement | ✅ draft; ⏳ rewrite appendix answers in my own words |
| Every reference actually read | ⏳ me |
| Five LinkedIn posts published | ⏳ me (drafts ready) |
| Reddit/X continued; discussion record updated | ⏳ me |
| At least one idea changed by external feedback, or an honest "none" | ⏳ me |
