"""
run_experiment.py - Run the baseline and all policies on the 40 cases and score them.

Steps:
  1. Load data/cases.csv (what the agent sees).
  2. Each policy decides. Labels are NOT loaded until all decisions are saved.
  3. Load data/labels.csv (feedback) and compute the metrics.

Outputs in results/:
  predictions_<policy>.csv   every decision, belief and action
  metrics.json / metrics.md  all scores
  confusion_<policy>.png     confusion matrix figures
"""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import agent  # noqa: E402

RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


def load(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def decide_all(cases):
    """Step 2: decisions only. No labels in memory."""
    out = {}
    for name, fn in agent.POLICIES.items():
        rows = []
        for c in cases:
            d = fn(c)
            row = {"case_id": c["case_id"], "service": c["service"],
                   "cost": c["cost"], "action": d["action"],
                   "investigated": d["investigated"]}
            if "belief" in d:
                for s in agent.STATES:
                    row[f"p_{s}"] = round(d["belief"][s], 4)
                row["spike_ratio"] = round(d["obs"]["ratio"], 2)
                row["region_new"] = d["obs"]["region_new"]
            if "z" in d:
                row["z"] = d["z"]
            rows.append(row)
        out[name] = rows
        with open(RESULTS / f"predictions_{name}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    return out


def score(rows, labels):
    """Step 3: feedback - compare decisions with the hidden truth."""
    truth = {l["case_id"]: l["true_state"] for l in labels}
    conf = {s: {a: 0 for a in agent.ACTIONS} for s in agent.STATES}
    total_cost, correct, tp, fp, fn, tn, n_inv = 0, 0, 0, 0, 0, 0, 0
    brier = []
    for r in rows:
        s, a = truth[r["case_id"]], r["action"]
        conf[s][a] += 1
        cost = agent.COST[a][s] + (agent.INVESTIGATE_COST if r["investigated"] else 0)
        total_cost += cost
        r["true_state"], r["decision_cost"] = s, cost
        correct += a == agent.BEST_ACTION[s]
        n_inv += bool(r["investigated"])
        # "problem" = Waste or Compromise; "alert" = Report or Limit
        problem, alert = s in ("Waste", "Compromise"), a in ("Report", "Limit")
        tp += problem and alert
        fp += (not problem) and alert
        fn += problem and (not alert)
        tn += (not problem) and (not alert)
        if "p_Normal" in r:
            brier.append(sum((r[f"p_{x}"] - (x == s)) ** 2 for x in agent.STATES))
    n = len(rows)
    m = {
        "n_cases": n,
        "correct_action_rate": round(correct / n, 3),
        "precision": round(tp / (tp + fp), 3) if tp + fp else None,
        "recall": round(tp / (tp + fn), 3) if tp + fn else None,
        "false_positives": fp,
        "false_negatives": fn,
        "missed_compromises": conf["Compromise"]["Ignore"],
        "limit_on_planned_or_normal": conf["Planned"]["Limit"] + conf["Normal"]["Limit"],
        "human_review_rate": round(sum(r["action"] == "Report" for r in rows) / n, 3),
        "investigate_rate": round(n_inv / n, 3),
        "total_decision_cost_usd": total_cost,
        "avg_decision_cost_usd": round(total_cost / n, 2),
        "brier_score": round(sum(brier) / len(brier), 3) if brier else None,
        "confusion": conf,
    }
    return m


def plot_confusion(name, conf):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    data = [[conf[s][a] for a in agent.ACTIONS] for s in agent.STATES]
    fig, ax = plt.subplots(figsize=(4, 3.3))
    ax.imshow(data, cmap="Blues")
    ax.set_xticks(range(3), agent.ACTIONS)
    ax.set_yticks(range(4), agent.STATES)
    ax.set_xlabel("Agent action")
    ax.set_ylabel("True state")
    ax.set_title(name.replace("_", " "), fontsize=10)
    for i, row in enumerate(data):
        for j, v in enumerate(row):
            ax.text(j, i, v, ha="center", va="center",
                    color="white" if v > 6 else "black")
    fig.tight_layout()
    fig.savefig(RESULTS / f"confusion_{name}.png", dpi=200)
    plt.close(fig)


def main():
    cases = load(ROOT / "data" / "cases.csv")
    decisions = decide_all(cases)                 # labels not loaded yet
    labels = load(ROOT / "data" / "labels.csv")   # feedback

    all_m = {"run_time_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "policy_version": agent.POLICY_VERSION, "policies": {}}
    for name, rows in decisions.items():
        m = score(rows, labels)
        all_m["policies"][name] = m
        plot_confusion(name, m["confusion"])
        with open(RESULTS / f"predictions_{name}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)

    (RESULTS / "metrics.json").write_text(json.dumps(all_m, indent=2))

    keys = ["correct_action_rate", "precision", "recall", "false_positives",
            "false_negatives", "missed_compromises", "limit_on_planned_or_normal",
            "human_review_rate", "investigate_rate", "total_decision_cost_usd",
            "avg_decision_cost_usd", "brier_score"]
    lines = ["| Metric | " + " | ".join(all_m["policies"]) + " |",
             "|---|" + "---|" * len(all_m["policies"])]
    for k in keys:
        lines.append(f"| {k} | " + " | ".join(str(m[k]) for m in all_m["policies"].values()) + " |")
    table = "\n".join(lines)
    (RESULTS / "metrics.md").write_text(f"# Results ({all_m['run_time_utc']})\n\n{table}\n")
    print(table)


if __name__ == "__main__":
    main()
