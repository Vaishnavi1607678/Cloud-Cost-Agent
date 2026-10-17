"""
run_v2.py - Compare v1 and v2 on the development set (seed 42) and on a
NEW holdout set (seed 2026) that was created after the v1 failure analysis.

v2 was designed by looking at the development-set failures, so the holdout
result is the fair one.

Decisions are made one case at a time. The true label of a case is revealed
only AFTER the agent has decided (feedback), and the learning agent may then
update itself before the next case.

Outputs: results/v2_metrics.md, results/v2_metrics.json,
         results/predictions_<set>_<policy>.csv
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import agent as v1          # noqa: E402
import agent_v2 as v2       # noqa: E402
from run_experiment import score, load, plot_confusion, RESULTS   # noqa: E402

SETS = {"dev": ("cases.csv", "labels.csv"),
        "holdout": ("cases_holdout.csv", "labels_holdout.csv")}


def run_policy(name, cases, labels):
    truth = {l["case_id"]: l["true_state"] for l in labels}
    model = None
    if name.startswith("v2"):
        model = v2.Model(learn=(name == "v2_full"))
    rows = []
    for c in cases:
        # ---- decision (label not used) ----
        if name == "Baseline":
            d = v1.policy_baseline(c)
        elif name == "Baseline_usage":
            d = v1.policy_baseline_usage(c)
        elif name == "v1_C":
            d = v1.policy_C(c)
        else:
            d = v2.decide(model, c)
        row = {"case_id": c["case_id"], "service": c["service"], "cost": c["cost"],
               "action": d["action"], "investigated": d["investigated"],
               "guarded": d.get("guarded", False)}
        if "belief" in d:
            for s in v1.STATES:
                row[f"p_{s}"] = round(d["belief"][s], 4)
        rows.append(row)
        # ---- feedback (label revealed after the decision) ----
        if model is not None:
            model.feedback(truth[c["case_id"]], d["obs"], d["paid_clues"])
    return rows


def main():
    policies = ["Baseline", "v1_C", "v2_no_learning", "v2_full"]
    out = {"policy_version": v2.POLICY_VERSION, "sets": {}}
    keys = ["correct_action_rate", "precision", "recall", "false_positives",
            "false_negatives", "missed_compromises", "limit_on_planned_or_normal",
            "human_review_rate", "investigate_rate", "total_decision_cost_usd",
            "avg_decision_cost_usd", "brier_score"]
    md = ["# v1 vs v2 results", ""]
    for set_name, (cf, lf) in SETS.items():
        cases, labels = load(ROOT / "data" / cf), load(ROOT / "data" / lf)
        out["sets"][set_name] = {}
        for p in policies:
            rows = run_policy(p, cases, labels)
            m = score(rows, labels)
            out["sets"][set_name][p] = m
            with open(RESULTS / f"predictions_{set_name}_{p}.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
            if set_name == "holdout":
                plot_confusion(f"holdout_{p}", m["confusion"])
        md += [f"## {set_name} set", "",
               "| Metric | " + " | ".join(policies) + " |",
               "|---|" + "---|" * len(policies)]
        for k in keys:
            md.append(f"| {k} | " + " | ".join(str(out['sets'][set_name][p][k]) for p in policies) + " |")
        md.append("")
    (RESULTS / "v2_metrics.json").write_text(json.dumps(out, indent=2))
    (RESULTS / "v2_metrics.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
