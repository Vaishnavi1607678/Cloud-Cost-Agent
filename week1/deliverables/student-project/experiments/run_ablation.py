"""
run_ablation.py - Which v2 change matters? Turn on one change at a time
(no learning) over the same 30 random case sets as run_seeds.py.

Output: results/ablation.md
"""
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import agent_v2 as v2                             # noqa: E402
import make_cases                                 # noqa: E402
from run_experiment import score, RESULTS         # noqa: E402
from run_v2 import run_policy                     # noqa: E402
from run_seeds import SEEDS                       # noqa: E402

VARIANTS = {   # (usage ratio, free owner tag, limit guard)
    "none (= v1 C with v2 code)": (False, False, False),
    "+ usage ratio only": (True, False, False),
    "+ free owner tag only": (False, True, False),
    "+ limit guard only": (False, False, True),
    "all three (v2_no_learning)": (True, True, True),
}
KEYS = ["total_decision_cost_usd", "recall", "false_positives",
        "missed_compromises", "limit_on_planned_or_normal", "human_review_rate"]


def main():
    lines = ["# Ablation: effect of each v2 change (mean over 30 case sets, no learning)", "",
             "| Variant | " + " | ".join(KEYS) + " |", "|---|" + "---|" * len(KEYS)]
    for name, (u, t, g) in VARIANTS.items():
        v2.USE_USAGE_RATIO, v2.FREE_OWNER_TAG, v2.USE_LIMIT_GUARD = u, t, g
        acc = {k: [] for k in KEYS}
        for seed in SEEDS:
            cases, labels = make_cases.build(seed)
            m = score(run_policy("v2_no_learning", cases, labels), labels)
            for k in KEYS:
                acc[k].append(m[k])
        lines.append(f"| {name} | " + " | ".join(f"{statistics.mean(acc[k]):.2f}" for k in KEYS) + " |")
    v2.USE_USAGE_RATIO = v2.FREE_OWNER_TAG = v2.USE_LIMIT_GUARD = True
    (RESULTS / "ablation.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
