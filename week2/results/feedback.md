# Feedback asymmetry: learning the prior from what the agent hears back

World: {'Normal': 0.73, 'Planned': 0.08, 'Waste': 0.12, 'Compromise': 0.03, 'Other': 0.04} (hypothetical). Agent starts from {'Normal': 0.78, 'Planned': 0.08, 'Waste': 0.07, 'Compromise': 0.03, 'Other': 0.04}. Policy: P2 with stakes. 5000 cases x 5 seeds, mean.

| Regime | Cases seen | Learned P(Waste) (true 0.12) | Learned P(Compromise) (true 0.03) | KL(world || learned prior) |
|---|---|---|---|---|
| full | 500 | 0.1193 | 0.0300 | 0.0040 |
| full | 1000 | 0.1205 | 0.0271 | 0.0037 |
| full | 2000 | 0.1221 | 0.0285 | 0.0010 |
| full | 3000 | 0.1211 | 0.0286 | 0.0008 |
| full | 5000 | 0.1203 | 0.0295 | 0.0005 |
| asymmetric | 500 | 0.1043 | 0.0300 | 0.0165 |
| asymmetric | 1000 | 0.1029 | 0.0269 | 0.0157 |
| asymmetric | 2000 | 0.1023 | 0.0280 | 0.0148 |
| asymmetric | 3000 | 0.1010 | 0.0281 | 0.0147 |
| asymmetric | 5000 | 0.0999 | 0.0292 | 0.0154 |
| audit 5% | 500 | 0.1087 | 0.0305 | 0.0164 |
| audit 5% | 1000 | 0.1128 | 0.0273 | 0.0082 |
| audit 5% | 2000 | 0.1137 | 0.0284 | 0.0035 |
| audit 5% | 3000 | 0.1135 | 0.0283 | 0.0045 |
| audit 5% | 5000 | 0.1165 | 0.0296 | 0.0025 |

| Regime | Missed waste (of ~600) | Missed compromises (of ~150) | Total cost |
|---|---|---|---|
| full | 96.6 | 1.6 | $201,667 |
| asymmetric | 104.2 | 1.8 | $202,489 |
| audit 5% | 99.6 | 1.8 | $202,562 |

Reading: with asymmetric feedback the agent only hears about the problems it already caught, so every missed problem is silently counted as Normal and the learned prior drifts away from the truth instead of towards it. Auditing a random 5% of ignored cases, and weighting each audited case by 1/0.05, removes most of that bias. In this setting the biased prior changes the total cost only a little, because P2 decides mostly from the evidence; the damage is that the agent's picture of the world is wrong and does not correct itself.
