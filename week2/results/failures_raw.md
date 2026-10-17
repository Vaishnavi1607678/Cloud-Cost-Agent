# Wrong decisions of P3 on the main 500 cases (seed 42)

146 wrong decisions. By (true state, action): Normal->Report: 113, Planned->Report: 15, Other->Ignore: 6, Waste->Ignore: 4, Compromise->Report: 3, Other->Report: 2, Normal->Limit: 1, Waste->Report: 1, Waste->Limit: 1

Top 15 by extra cost:

## S0126: true Waste, $509.03/day, P3 chose Ignore (best: Report), extra cost $3,362
- Free evidence: spike=high, price_jump=no, region_new=seen, owner_tag=tagged
- Paid checks bought: ticket=found, launcher=known (stop: remaining checks not worth their cost)
- Never bought: ask_owner=not_intended, forensics=clean
- Final belief: Normal 0.237, Planned 0.726, Waste 0.031, Compromise 0.001, Other 0.006
- After design changes: P3b -> Report, P3c -> Report

## S0214: true Waste, $83.84/day, P3 chose Ignore (best: Report), extra cost $519
- Free evidence: spike=low, price_jump=no, region_new=seen, owner_tag=tagged
- Paid checks bought: none (stop: no paid check has positive value)
- Never bought: launcher=known, ticket=none, ask_owner=not_intended, forensics=clean
- Final belief: Normal 0.968, Planned 0.015, Waste 0.013, Compromise 0.000, Other 0.004
- After design changes: P3b -> Ignore, P3c -> Ignore

## S0116: true Compromise, $65.08/day, P3 chose Report (best: Limit), extra cost $502
- Free evidence: spike=high, price_jump=no, region_new=seen, owner_tag=untagged
- Paid checks bought: launcher=known (stop: remaining checks not worth their cost)
- Never bought: ticket=none, ask_owner=intended, forensics=malicious
- Final belief: Normal 0.357, Planned 0.217, Waste 0.340, Compromise 0.081, Other 0.006
- After design changes: P3b -> Report, P3c -> Report

## S0023: true Compromise, $38.67/day, P3 chose Report (best: Limit), extra cost $502
- Free evidence: spike=low, price_jump=no, region_new=new, owner_tag=tagged
- Paid checks bought: launcher=unknown (stop: remaining checks not worth their cost)
- Never bought: ticket=none, ask_owner=not_intended, forensics=malicious
- Final belief: Normal 0.905, Planned 0.014, Waste 0.035, Compromise 0.045, Other 0.001
- After design changes: P3b -> Report, P3c -> Report

## S0480: true Compromise, $57.16/day, P3 chose Report (best: Limit), extra cost $500
- Free evidence: spike=med, price_jump=no, region_new=seen, owner_tag=untagged
- Paid checks bought: none (stop: no paid check has positive value)
- Never bought: launcher=unknown, ticket=none, ask_owner=not_intended, forensics=malicious
- Final belief: Normal 0.385, Planned 0.134, Waste 0.430, Compromise 0.042, Other 0.009
- After design changes: P3b -> Report, P3c -> Report

## S0081: true Normal, $43.79/day, P3 chose Limit (best: Ignore), extra cost $301
- Free evidence: spike=low, price_jump=no, region_new=new, owner_tag=untagged
- Paid checks bought: launcher=unknown (stop: remaining checks not worth their cost)
- Never bought: ticket=none, ask_owner=not_intended, forensics=clean
- Final belief: Normal 0.261, Planned 0.006, Waste 0.075, Compromise 0.658, Other 0.000
- After design changes: P3b -> Limit, P3c -> Report

## S0378: true Other, $147.05/day, P3 chose Ignore (best: Report), extra cost $216
- Free evidence: spike=low, price_jump=yes, region_new=seen, owner_tag=untagged
- Paid checks bought: launcher=known (stop: remaining checks not worth their cost)
- Never bought: ticket=none, ask_owner=intended, forensics=clean
- Final belief: Normal 0.790, Planned 0.009, Waste 0.032, Compromise 0.001, Other 0.168
- After design changes: P3b -> Report, P3c -> Report

## S0141: true Other, $137.55/day, P3 chose Ignore (best: Report), extra cost $199
- Free evidence: spike=low, price_jump=yes, region_new=seen, owner_tag=tagged
- Paid checks bought: none (stop: no paid check has positive value)
- Never bought: launcher=known, ticket=none, ask_owner=not_intended, forensics=clean
- Final belief: Normal 0.816, Planned 0.006, Waste 0.005, Compromise 0.000, Other 0.173
- After design changes: P3b -> Ignore, P3c -> Ignore

## S0153: true Other, $100.93/day, P3 chose Ignore (best: Report), extra cost $138
- Free evidence: spike=low, price_jump=yes, region_new=seen, owner_tag=tagged
- Paid checks bought: none (stop: no paid check has positive value)
- Never bought: launcher=known, ticket=none, ask_owner=intended, forensics=clean
- Final belief: Normal 0.816, Planned 0.006, Waste 0.005, Compromise 0.000, Other 0.173
- After design changes: P3b -> Ignore, P3c -> Ignore

## S0103: true Planned, $694.54/day, P3 chose Report (best: Ignore), extra cost $96
- Free evidence: spike=high, price_jump=no, region_new=new, owner_tag=untagged
- Paid checks bought: ticket=found, launcher=known, ask_owner=intended (stop: remaining checks not worth their cost)
- Never bought: forensics=clean
- Final belief: Normal 0.154, Planned 0.792, Waste 0.033, Compromise 0.020, Other 0.001
- After design changes: P3b -> Report, P3c -> Report

## S0168: true Normal, $208.36/day, P3 chose Report (best: Ignore), extra cost $91
- Free evidence: spike=med, price_jump=no, region_new=new, owner_tag=untagged
- Paid checks bought: launcher=known, ask_owner=not_intended (stop: remaining checks not worth their cost)
- Never bought: ticket=none, forensics=clean
- Final belief: Normal 0.062, Planned 0.011, Waste 0.497, Compromise 0.429, Other 0.001
- After design changes: P3b -> Report, P3c -> Report

## S0184: true Other, $69.49/day, P3 chose Ignore (best: Report), extra cost $86
- Free evidence: spike=low, price_jump=no, region_new=seen, owner_tag=tagged
- Paid checks bought: none (stop: no paid check has positive value)
- Never bought: launcher=known, ticket=none, ask_owner=intended, forensics=clean
- Final belief: Normal 0.968, Planned 0.015, Waste 0.013, Compromise 0.000, Other 0.004
- After design changes: P3b -> Ignore, P3c -> Ignore

## S0136: true Other, $55.78/day, P3 chose Ignore (best: Report), extra cost $63
- Free evidence: spike=low, price_jump=yes, region_new=seen, owner_tag=tagged
- Paid checks bought: none (stop: no paid check has positive value)
- Never bought: launcher=known, ticket=none, ask_owner=intended, forensics=clean
- Final belief: Normal 0.816, Planned 0.006, Waste 0.005, Compromise 0.000, Other 0.173
- After design changes: P3b -> Ignore, P3c -> Ignore

## S0289: true Planned, $402.53/day, P3 chose Report (best: Ignore), extra cost $56
- Free evidence: spike=med, price_jump=no, region_new=seen, owner_tag=tagged
- Paid checks bought: ticket=found, launcher=unknown (stop: remaining checks not worth their cost)
- Never bought: ask_owner=intended, forensics=clean
- Final belief: Normal 0.307, Planned 0.538, Waste 0.140, Compromise 0.005, Other 0.010
- After design changes: P3b -> Report, P3c -> Report

## S0007: true Normal, $38.45/day, P3 chose Report (best: Ignore), extra cost $55
- Free evidence: spike=med, price_jump=no, region_new=seen, owner_tag=tagged
- Paid checks bought: ticket=none (stop: remaining checks not worth their cost)
- Never bought: launcher=known, ask_owner=not_intended, forensics=clean
- Final belief: Normal 0.817, Planned 0.040, Waste 0.124, Compromise 0.002, Other 0.017
- After design changes: P3b -> Ignore, P3c -> Ignore

