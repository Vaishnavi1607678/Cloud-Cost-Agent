"""common.py - shared helpers for the Week 2 experiments."""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import evaluate as E   # noqa: E402
import model as M      # noqa: E402
import policies as P   # noqa: E402
import simulate as S   # noqa: E402

RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)
SEED, N = 42, 500

# name -> (policy function, agent settings)
POLICY_SET = {
    "P0 baseline":        (P.p0, {}),
    "P1 belief only":     (P.p1, {}),
    "P2 threshold":       (P.p2, {}),
    "P3 value of info":   (P.p3, {}),
    "P3b VOI + stakes":   (P.p3, {"scaled_costs": True}),
    "P3c + guard 0.7":    (P.p3, {"scaled_costs": True, "limit_guard": 0.7}),
}


def run(cases, fn, agent_kwargs, **score_kw):
    agent = P.Agent(**agent_kwargs)
    decisions = [fn(agent, c) for c in cases]          # decisions first ...
    return decisions, E.score(cases, decisions, **score_kw)   # ... truth only after


def save_predictions(path, cases, decisions):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "amount", "action", "checks"] + [f"p_{s}" for s in M.STATES] + ["true_state"])
        for c, d in zip(cases, decisions):
            w.writerow([c["case_id"], c["amount"], d["action"], "+".join(d["checks"])]
                       + [round(d["belief"].get(s, 0.0), 4) for s in M.STATES] + [c["true_state"]])


def fmt(x, money=False):
    if isinstance(x, float):
        return f"${x:,.0f}" if money else f"{x:.3f}"
    return str(x)


def table(results, keys, money=()):
    names = list(results)
    lines = ["| Metric | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for k in keys:
        lines.append(f"| {k} | " + " | ".join(fmt(results[n][k], k in money) for n in names) + " |")
    return "\n".join(lines)


def dump(name, obj):
    (RESULTS / name).write_text(json.dumps(obj, indent=2, default=float))
