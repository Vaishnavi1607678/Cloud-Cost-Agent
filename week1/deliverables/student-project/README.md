# Cloud Cost Agent — Week 1 AI-Native Project

**Problem:** The agent observes a daily AWS cost line item (service, region, usage, cost) and that service's recent history. It must choose to ignore, investigate, limit, or report the cost because the cause of the cost change is not known.

**Hidden states:** Normal · Planned spike · Waste/misconfiguration · Compromise
**Actions:** Ignore · Report (to a human) · Limit (budget action / scale down) · Investigate (check owner tag, CloudTrail launcher, change ticket)

## How to repeat the test

Requirements: Python 3.9+. `matplotlib` is optional (only for the confusion-matrix figures).

```bash
cd week1/deliverables/student-project
pip install matplotlib            # optional
python3 src/make_cases.py                          # dev set: data/cases.csv + labels.csv (seed 42)
python3 src/make_cases.py --seed 2026 --tag holdout  # holdout set used to test v2 fairly
python3 experiments/run_experiment.py              # v1: baseline + policies A, B, C on the dev set
python3 experiments/run_v2.py                      # v1 vs v2 on dev and holdout sets
python3 experiments/run_seeds.py                   # robustness: 30 random case sets
python3 experiments/run_ablation.py                # which v2 change matters
python3 experiments/run_sensitivity.py             # what if my cost/prior guesses are wrong
python3 experiments/run_calibration.py             # are the probabilities honest
python3 experiments/make_figures.py                # paper figure
```

To build the paper: copy `ijcai26.sty` and `named.bst` from the [IJCAI-ECAI 2026 author kit](https://www.ijcai.org/authors_kit) into `paper/`, then run `pdflatex main && bibtex main && pdflatex main && pdflatex main` (or upload the `paper/` folder to Overleaf).

The results appear in `results/`:
- `metrics.md` / `metrics.json` contain all scores
- `predictions_<policy>.csv` has every decision with its beliefs
- `confusion_<policy>.png` holds the confusion matrices
- `v2_metrics.md`, `seeds_metrics.md`, `ablation.md` contain the v2, robustness, and ablation results
- `failure-analysis.md` names and explains 8 failure conditions

All random seeds are fixed (42 for dev, 2026 for holdout, 1000–1029 for robustness), so the results are identical on every run.

## Files

| Path | Purpose |
|---|---|
| `data/aws_billing_data_mock.csv` | Mock AWS billing data: 150 rows, 5 services, Jul 2025 |
| `src/make_cases.py` | Builds 40 labeled simulated cases (14 Normal, 10 Planned, 9 Waste, 7 Compromise) |
| `src/agent.py` | v1: beliefs, Bayes update, cost table, baseline and 3 policies |
| `src/agent_v2.py` | v2: usage-ratio signal, free owner-tag check, learning from feedback, human guard on Limit |
| `experiments/run_experiment.py` | Runs v1 policies; loads labels only after all decisions are saved |
| `experiments/run_v2.py` | Runs v1 vs v2 one case at a time; each label is revealed only after the decision (feedback) |
| `experiments/run_seeds.py` | Repeats the test on 30 random case sets |
| `experiments/run_ablation.py` | Switches each v2 change on one at a time |
| `experiments/run_sensitivity.py` | Changes one cost/prior assumption at a time (review P4, Q1) |
| `experiments/run_calibration.py` | Calibration table and ECE (review Q4) |
| `experiments/make_figures.py` | Figure for the paper |
| `decisions/probability-decision-record.md` | Full Bayes calculation for one unlabeled real row |
| `paper/main.tex`, `paper/references.bib` | IJCAI-style preprint (draft PDF: `paper/preprint-draft.pdf`) |

## Policies compared

| Name | Rule |
|---|---|
| Baseline | Report if cost > mean + 2·std of the last 7 days, else Ignore |
| Baseline_usage | Report if the z-score of cost **or** usage > 2 (fairer baseline, added after review R3) |
| A_most_likely | Pick the most probable hidden state, then take that state's action |
| B_expected_cost | Pick the action with the lowest expected dollar cost |
| C_expected_cost_investigate | Like B, but first investigates when the expected cost after investigating (including the $25 check) is lower; then updates the belief with Bayes' rule |

## v2 (changed after the failure analysis)

| Change | Reason (failure) |
|---|---|
| Spike = max(cost ratio, usage ratio) | F2: usage spike hidden by price noise |
| Owner tag is read automatically for free | F1: quiet compromise was never investigated |
| Learns likelihoods from feedback | Section 8 "Feedback" |
| Limit only if P(Compromise) ≥ 50% | Human control on the most harmful action |

Holdout result (seed 2026): total decision cost **$4,080 (v2)** vs **$6,260 (v1 C)** vs **$21,090 (baseline)**.
Over 30 random sets, v2 was cheaper than v1 in 25 of 30, but it raised more false alarms (14.2 vs 8.7 per 40 cases).

## Known limitations

- The billing data is mock data, and the anomalies are injected by my own assumptions. These are not real incidents.
- The cost table and likelihoods are my estimates and still need checking with practitioners.
- 40 cases is small, so the numbers are indicative only.

## Completion checklist (Section 16)

| Item | Status | Where |
|---|---|---|
| Use one problem for all project work | ✅ | Same problem statement everywhere |
| Create the AI research file | ✅ | `research-file.md` |
| Verify five to ten Reddit communities | ⏳ student | `research-file.md` §6 |
| Make two contributions in each Reddit community | ⏳ student | `discussion-record.md` |
| Complete five Reddit discussions | ⏳ student | `discussion-record.md` |
| Follow 15 to 25 relevant X accounts | ⏳ student | `research-file.md` §7 |
| Write three or four X comments each day | ⏳ student | `discussion-record.md` |
| Complete three X discussions | ⏳ student | `discussion-record.md` |
| Build a testable agent or simulation | ✅ | `src/agent.py`, `src/agent_v2.py` |
| Prepare 30 to 50 test cases | ✅ | 40 per set (`data/`) |
| Compare two agent policies | ✅ | A, B, C, v2 |
| Compare the agent with one baseline | ✅ | Threshold + threshold-with-usage |
| Examine five incorrect decisions | ✅ | `results/failure-analysis.md` (8 named) |
| Create one probability decision record | ✅ | `decisions/probability-decision-record.md` |
| Complete three AI reviews | ✅ (+ Gemini review to add) | `review-record.md` |
| Record accepted and rejected AI review comments | ✅ | `review-record.md` (17 accepted, 4 rejected) |
| Write the preprint in LaTeX | ✅ draft (needs discussion results) | `paper/main.tex` |
| Compile the preprint PDF | ✅ draft; ⏳ final with official IJCAI style → `paper/preprint.pdf` | `paper/preprint-draft.pdf` |
| Publish one LinkedIn post with the PDF | ⏳ student (draft ready) | `social/linkedin-post.md` |
| Publish the PDF and a short thread on X | ⏳ student (draft ready) | `social/x-thread.md` |
| State AI use, human contributions, and limitations | ✅ | Paper, README, `research-file.md` §12 |
