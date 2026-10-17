"""
make_figures.py - Figures for the paper (paper/figures/).
Uses the same 30 random case sets as run_seeds.py.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))
import make_cases                                 # noqa: E402
from run_experiment import score                  # noqa: E402
from run_v2 import run_policy                     # noqa: E402
from run_seeds import SEEDS                       # noqa: E402

FIG = ROOT / "paper" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
POL = ["Baseline", "v1_C", "v2_full"]
LABEL = {"Baseline": "Threshold\nbaseline", "v1_C": "v1 (C)", "v2_full": "v2"}

cost = {p: [] for p in POL}
fp = {p: [] for p in POL}
miss = {p: [] for p in POL}
for seed in SEEDS:
    cases, labels = make_cases.build(seed)
    for p in POL:
        m = score(run_policy(p, cases, labels), labels)
        cost[p].append(m["total_decision_cost_usd"] / 1000)
        fp[p].append(m["false_positives"])
        miss[p].append(m["missed_compromises"])

fig, axes = plt.subplots(1, 3, figsize=(7, 2.4))
for ax, data, title in zip(axes, [cost, miss, fp],
                           ["Total decision cost (k$)", "Missed compromises", "False alarms"]):
    ax.boxplot([data[p] for p in POL], widths=0.55, showfliers=False,
               medianprops={"color": "#c0392b"})
    ax.set_xticks(range(1, 4), [LABEL[p] for p in POL], fontsize=7)
    ax.set_title(title, fontsize=8)
    ax.tick_params(axis="y", labelsize=7)
    ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / "results_boxplot.pdf")
fig.savefig(FIG / "results_boxplot.png", dpi=200)
print("saved", FIG / "results_boxplot.pdf")
