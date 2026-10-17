"""
make_figures.py - Figures for the Week 2 paper (paper/figures/).
Figure 1: accuracy vs total cost vs human review per policy (20 seeds, from results/robustness.json)
Figure 2: (a) information gain vs net value of information for each paid check, at the
          example belief of the belief-state table; (b) JSD alarm detection rate vs window size.
"""
import json
import statistics as st

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common import M, RESULTS, ROOT

FIG = ROOT / "paper" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
rob = json.loads((RESULTS / "robustness.json").read_text())["matched"]
pols = ["P0 baseline", "P1 belief only", "P2 threshold", "P3 value of info", "P3b VOI + stakes", "P3c + guard 0.7"]
short = ["P0", "P1", "P2", "P3", "P3b", "P3c"]

fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.3))
for a, key, title, scale in [(ax[0], "accuracy", "Accuracy", 1), (ax[1], "total_cost", "Total cost (k$, log)", 1e-3),
                             (ax[2], "human_review_rate", "Human-review rate", 1)]:
    m = [st.mean(rob[p][key]) * scale for p in pols]
    s = [st.stdev(rob[p][key]) * scale for p in pols]
    a.bar(short, m, yerr=s, color=["#999999", "#999999", "#5b8bd0", "#5b8bd0", "#2b5797", "#2b5797"], capsize=2)
    a.set_title(title, fontsize=8)
    a.tick_params(labelsize=7)
    if key == "total_cost":
        a.set_yscale("log")
    a.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(FIG / "fig1_policies.pdf")
fig.savefig(FIG / "fig1_policies.png", dpi=200)

# Figure 2a: info gain vs value at the example belief
b = dict(M.PRIOR)
for ev, o in {"spike": "high", "price_jump": "no", "region_new": "seen", "owner_tag": "untagged"}.items():
    b = M.update(b, ev, o)
c, h = M.cost_table(M.A0), M.hourly_loss(M.A0)
fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.5))
for ev in M.PAID:
    ig = M.info_gain(b, ev)
    v = M.value_of_information(b, ev, c, h)["net"]
    ax[0].scatter(ig, v, s=25, color="#2b5797")
    ax[0].annotate(f"{ev}\n(${M.EVIDENCE[ev]['price']:,.0f})", (ig, v), fontsize=6.5, xytext=(4, 2), textcoords="offset points")
ax[0].axhline(0, color="#c0392b", lw=0.8)
ax[0].set_ylim(-8000, 400)
ax[0].set_xlim(0.2, 0.72)
ax[0].set_yscale("symlog", linthresh=10)
ax[0].set_xlabel("Expected information gain (bits)", fontsize=7)
ax[0].set_ylabel("Net value of information ($)", fontsize=7)
ax[0].set_title("More bits is not more value", fontsize=8)
ax[0].tick_params(labelsize=7)
# Figure 2b: JSD detection, parsed from results/generalization.md
rows = [l for l in (RESULTS / "generalization.md").read_text().splitlines() if l.startswith("| 1") or l.startswith("| 2") or l.startswith("| 5")]
sizes, det = [], []
for l in rows:
    parts = [x.strip() for x in l.strip("|").split("|")]
    if len(parts) == 6 and parts[0].isdigit():
        sizes.append(int(parts[0]))
        det.append(float(parts[5]))
ax[1].plot(sizes, det, marker="o", color="#2b5797")
ax[1].axhline(0.01, color="#999999", lw=0.8, ls="--")
ax[1].set_xscale("log")
ax[1].set_xticks(sizes, [str(s) for s in sizes])
ax[1].set_xlabel("Window size (cases)", fontsize=7)
ax[1].set_ylabel("Shift detection rate", fontsize=7)
ax[1].set_title("JSD alarm: startup -> enterprise", fontsize=8)
ax[1].tick_params(labelsize=7)
fig.tight_layout()
fig.savefig(FIG / "fig2_information.pdf")
fig.savefig(FIG / "fig2_information.png", dpi=200)
print("saved figures")
