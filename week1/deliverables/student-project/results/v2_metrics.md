# v1 vs v2 results

## dev set

| Metric | Baseline | v1_C | v2_no_learning | v2_full |
|---|---|---|---|---|
| correct_action_rate | 0.55 | 0.675 | 0.55 | 0.525 |
| precision | 0.571 | 0.619 | 0.533 | 0.517 |
| recall | 0.5 | 0.812 | 1.0 | 0.938 |
| false_positives | 6 | 8 | 14 | 14 |
| false_negatives | 8 | 3 | 0 | 1 |
| missed_compromises | 3 | 1 | 0 | 0 |
| limit_on_planned_or_normal | 0 | 0 | 0 | 0 |
| human_review_rate | 0.35 | 0.425 | 0.625 | 0.6 |
| investigate_rate | 0.0 | 0.525 | 0.2 | 0.225 |
| total_decision_cost_usd | 19860 | 8605 | 3480 | 3865 |
| avg_decision_cost_usd | 496.5 | 215.12 | 87.0 | 96.62 |
| brier_score | None | 0.653 | 0.602 | 0.645 |

## holdout set

| Metric | Baseline | v1_C | v2_no_learning | v2_full |
|---|---|---|---|---|
| correct_action_rate | 0.4 | 0.55 | 0.5 | 0.6 |
| precision | 0.357 | 0.5 | 0.469 | 0.5 |
| recall | 0.312 | 0.688 | 0.938 | 0.875 |
| false_positives | 9 | 11 | 17 | 14 |
| false_negatives | 11 | 5 | 1 | 2 |
| missed_compromises | 3 | 0 | 0 | 0 |
| limit_on_planned_or_normal | 0 | 1 | 1 | 1 |
| human_review_rate | 0.35 | 0.4 | 0.65 | 0.5 |
| investigate_rate | 0.0 | 0.4 | 0.075 | 0.15 |
| total_decision_cost_usd | 21090 | 6260 | 4795 | 4080 |
| avg_decision_cost_usd | 527.25 | 156.5 | 119.88 | 102.0 |
| brier_score | None | 0.73 | 0.591 | 0.576 |
