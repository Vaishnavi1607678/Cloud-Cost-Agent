# Ablation: effect of each v2 change (mean over 30 case sets, no learning)

| Variant | total_decision_cost_usd | recall | false_positives | missed_compromises | limit_on_planned_or_normal | human_review_rate |
|---|---|---|---|---|---|---|
| none (= v1 C with v2 code) | 6656.33 | 0.76 | 8.67 | 0.57 | 0.03 | 0.38 |
| + usage ratio only | 4732.17 | 0.86 | 11.07 | 0.23 | 0.03 | 0.47 |
| + free owner tag only | 4501.83 | 0.88 | 12.70 | 0.10 | 0.20 | 0.55 |
| + limit guard only | 7073.00 | 0.76 | 8.67 | 0.57 | 0.03 | 0.40 |
| all three (v2_no_learning) | 3837.50 | 0.93 | 15.70 | 0.03 | 0.23 | 0.62 |
