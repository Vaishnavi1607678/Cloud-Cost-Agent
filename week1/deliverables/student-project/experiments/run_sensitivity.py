"""
run_sensitivity.py - Do the conclusions survive if my guessed numbers are wrong?
(Requested by the practitioner and probability reviews, see review-record.md.)

Changes one assumption at a time, over the same 30 random case sets:
  - Report cost for Normal/Planned (alert fatigue): $50 -> $150 -> $400
  - Cost of ignoring a compromise: $5,000 -> $2,000 -> $20,000
  - Prior P(Compromise): 4% -> 1% -> 10%  (taken from Normal)
The agent's decisions AND the scoring both use the changed number.

Output: results/sensitivity.md
"""
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import agent as v1                                # noqa: E402
import agent_v2 as v2                             # noqa: E402
import make_cases                                 # noqa: E402
from run_experiment import score, RESULTS         # noqa: E402
from run_v2 import run_policy                     # noqa: E402
from run_seeds import SEEDS                       # noqa: E402

POLICIES = ["Baseline", "v1_C", "v2_full"]
BASE_COST = {a: dict(v1.COST[a]) for a in v1.COST}
BASE_PRIOR_V1, BASE_PRIOR_V2 = dict(v1.PRIOR), dict(v2.PRIOR)


def set_assumptions(report_fp=50, ignore_c=5000, prior_c=0.04):
    for a in BASE_COST:                           # mutate in place: v1 and v2 share COST
        v1.COST[a].update(BASE_COST[a])
    v1.COST["Report"]["Normal"] = v1.COST["Report"]["Planned"] = report_fp
    v1.COST["Ignore"]["Compromise"] = ignore_c
    for prior in (v1.PRIOR, v2.PRIOR):
        prior.update(BASE_PRIOR_V1)
        prior["Normal"] = 0.80 - (prior_c - 0.04)
        prior["Compromise"] = prior_c
    v1.BEST_ACTION.update({s: min(v1.ACTIONS, key=lambda a: v1.COST[a][s]) for s in v1.STATES})


def run():
    out = {}
    for p in POLICIES:
        acc = {"cost": [], "fp": [], "missed": [], "review": []}
        for seed in SEEDS:
            cases, labels = make_cases.build(seed)
            m = score(run_policy(p, cases, labels), labels)
            acc["cost"].append(m["total_decision_cost_usd"])
            acc["fp"].append(m["false_positives"])
            acc["missed"].append(m["missed_compromises"])
            acc["review"].append(m["human_review_rate"])
        out[p] = {k: statistics.mean(v) for k, v in acc.items()}
    return out


SCENARIOS = [
    ("Default (Report $50, ignore-compromise $5,000, prior 4%)", {}),
    ("Alert fatigue: Report on Normal/Planned = $150", {"report_fp": 150}),
    ("Strong alert fatigue: Report on Normal/Planned = $400", {"report_fp": 400}),
    ("Cheaper compromise: Ignore-compromise = $2,000", {"ignore_c": 2000}),
    ("Worse compromise: Ignore-compromise = $20,000", {"ignore_c": 20000}),
    ("Rarer compromise: prior 1%", {"prior_c": 0.01}),
    ("More common compromise: prior 10%", {"prior_c": 0.10}),
]


def main():
    lines = ["# Sensitivity analysis (mean over 30 case sets of 40)", "",
             "Each cell: total decision cost $ / false alarms / missed compromises / human-review rate", "",
             "| Scenario | " + " | ".join(POLICIES) + " | v2 cheapest? |",
             "|---|" + "---|" * (len(POLICIES) + 1)]
    for name, kw in SCENARIOS:
        set_assumptions(**kw)
        r = run()
        cells = [f"${r[p]['cost']:,.0f} / {r[p]['fp']:.1f} / {r[p]['missed']:.2f} / {r[p]['review']:.2f}"
                 for p in POLICIES]
        best = min(POLICIES, key=lambda p: r[p]["cost"])
        lines.append(f"| {name} | " + " | ".join(cells) + f" | {'yes' if best == 'v2_full' else 'no (' + best + ')'} |")
    set_assumptions()
    (RESULTS / "sensitivity.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
