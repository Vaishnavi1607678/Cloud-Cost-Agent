"""
run_seeds.py - Robustness check. 40 cases is small, so one run can be luck.
Repeat the whole test on 30 new random case sets (seeds 1000-1029) and report
the mean and the 10th-90th percentile range of each metric.

Output: results/seeds_metrics.md
"""
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import make_cases                                   # noqa: E402
from run_experiment import score, RESULTS           # noqa: E402
from run_v2 import run_policy                       # noqa: E402

SEEDS = range(1000, 1030)
POLICIES = ["Baseline", "Baseline_usage", "v1_C", "v2_no_learning", "v2_full"]
KEYS = ["total_decision_cost_usd", "recall", "false_positives", "missed_compromises",
        "limit_on_planned_or_normal", "human_review_rate", "investigate_rate"]


def pct(xs, q):
    xs = sorted(xs)
    return xs[int(q * (len(xs) - 1))]


def main():
    res = {p: {k: [] for k in KEYS} for p in POLICIES}
    wins = 0
    for seed in SEEDS:
        cases, labels = make_cases.build(seed)
        costs = {}
        for p in POLICIES:
            m = score(run_policy(p, cases, labels), labels)
            for k in KEYS:
                res[p][k].append(m[k])
            costs[p] = m["total_decision_cost_usd"]
        wins += costs["v2_full"] < costs["v1_C"]
    lines = [f"# Robustness check: {len(SEEDS)} random case sets of 40 cases", "",
             "Mean (10th-90th percentile)", "",
             "| Metric | " + " | ".join(POLICIES) + " |", "|---|" + "---|" * len(POLICIES)]
    for k in KEYS:
        cells = []
        for p in POLICIES:
            xs = res[p][k]
            cells.append(f"{statistics.mean(xs):.2f} ({pct(xs, .1):.2f}-{pct(xs, .9):.2f})")
        lines.append(f"| {k} | " + " | ".join(cells) + " |")
    # Two-sided sign test: probability of a split at least this uneven if both were equally good
    from math import comb
    n, k = len(SEEDS), max(wins, len(SEEDS) - wins)
    p = min(1.0, 2 * sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n)
    lines += ["", f"v2_full had lower total decision cost than v1_C in {wins} of {len(SEEDS)} sets "
              f"(two-sided sign test p = {p:.5f})."]
    (RESULTS / "seeds_metrics.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
