"""
run_calibration.py - Are the agent's probabilities honest?
(Requested by the probability review, see review-record.md.)

For every decision over the 30 random case sets, take the agent's final
P(problem) = P(Waste) + P(Compromise), group by predicted value, and compare
with how often a problem was really there. A calibrated agent that says "70%"
should be right about 70% of the time.

Output: results/calibration.md
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import make_cases                                 # noqa: E402
from run_experiment import RESULTS                # noqa: E402
from run_v2 import run_policy                     # noqa: E402
from run_seeds import SEEDS                       # noqa: E402

BINS = [(0.0, 0.1), (0.1, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 1.01)]
POLICIES = ["v1_C", "v2_full"]


def main():
    lines = ["# Calibration of P(problem) = P(Waste) + P(Compromise)",
             "", f"All decisions over {len(SEEDS)} case sets ({len(SEEDS) * 40} cases).",
             "Test mix: 40% of cases are real problems (Waste or Compromise).", ""]
    for p in POLICIES:
        pairs = []
        for seed in SEEDS:
            cases, labels = make_cases.build(seed)
            truth = {l["case_id"]: l["true_state"] for l in labels}
            for r in run_policy(p, cases, labels):
                pred = r["p_Waste"] + r["p_Compromise"]
                pairs.append((pred, truth[r["case_id"]] in ("Waste", "Compromise")))
        ece = 0.0
        lines += [f"## {p}", "", "| Predicted P(problem) | Cases | Mean predicted | Observed rate |",
                  "|---|---|---|---|"]
        for lo, hi in BINS:
            b = [(q, y) for q, y in pairs if lo <= q < hi]
            if not b:
                lines.append(f"| {lo:.1f}–{min(hi, 1):.1f} | 0 | – | – |")
                continue
            mp = sum(q for q, _ in b) / len(b)
            ob = sum(y for _, y in b) / len(b)
            ece += len(b) / len(pairs) * abs(mp - ob)
            lines.append(f"| {lo:.1f}–{min(hi, 1):.1f} | {len(b)} | {mp:.2f} | {ob:.2f} |")
        lines += ["", f"Expected calibration error (ECE): **{ece:.3f}** (0 = perfect)", ""]
    (RESULTS / "calibration.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
