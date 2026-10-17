# Main experiment: 500 simulated cases, seed 42, matched simulator

True states in this sample: {'Normal': 399, 'Planned': 36, 'Waste': 27, 'Compromise': 16, 'Other': 22}

| Metric | P0 baseline | P1 belief only | P2 threshold | P3 value of info | P3b VOI + stakes | P3c + guard 0.7 |
|---|---|---|---|---|---|---|
| accuracy | 0.880 | 0.908 | 0.598 | 0.708 | 0.690 | 0.686 |
| precision | nan | 0.528 | 0.167 | 0.203 | 0.188 | 0.188 |
| recall | 0.000 | 0.651 | 0.907 | 0.860 | 0.837 | 0.837 |
| false_positives | 0 | 25 | 195 | 145 | 155 | 155 |
| false_negatives | 43 | 15 | 4 | 6 | 7 | 7 |
| missed_compromises | 16 | 2 | 1 | 0 | 0 | 0 |
| wrong_limits | 0 | 2 | 1 | 1 | 1 | 0 |
| decision_cost | $227,187 | $39,391 | $22,823 | $16,207 | $13,228 | $13,978 |
| info_cost | $0 | $0 | $0 | $984 | $344 | $344 |
| delay_cost | $0 | $0 | $0 | $312 | $301 | $301 |
| total_cost | $227,187 | $39,391 | $22,823 | $17,502 | $13,873 | $14,623 |
| questions_per_case | 0.000 | 0.000 | 0.000 | 0.520 | 0.270 | 0.270 |
| human_review_rate | 0.000 | 0.080 | 0.450 | 0.334 | 0.352 | 0.358 |
| cross_entropy_bits | 1.122 | 0.743 | 0.743 | 0.665 | 0.713 | 0.713 |
| ece | 0.014 | 0.025 | 0.025 | 0.024 | 0.016 | 0.016 |
