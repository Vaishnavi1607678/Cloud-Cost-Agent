"""
run_robustness.py - Is the main result luck? And what if the agent's model is wrong?

  Part A: 20 random seeds x 500 cases, matched simulator (all policies).
  Part B: 20 seeds x 500 cases, MISSPECIFIED simulator (stolen keys look like a known
          user 60% of the time; untagged and unknown-launcher come together for normal
          automation). The agent does not know this.
  Part C: design-change re-tests on the same seeds:
          DC1  P3 -> P3b  (losses depend on bill size)
          DC2  P3b without the residual 'Other' state -> with it (world contains Other)

Output: results/robustness.md, results/robustness.json
"""
import statistics as st

from common import N, POLICY_SET, RESULTS, S, P, dump, run

SEEDS = range(100, 120)
KEYS = ["accuracy", "recall", "false_positives", "missed_compromises", "wrong_limits",
        "total_cost", "info_cost", "questions_per_case", "human_review_rate", "cross_entropy_bits", "ece"]
VARIANTS = {**POLICY_SET,
            "P3b without Other": (P.p3, {"scaled_costs": True,
                                         "states": ["Normal", "Planned", "Waste", "Compromise"]})}


def collect(misspecified):
    out = {name: {k: [] for k in KEYS} for name in VARIANTS}
    for seed in SEEDS:
        cases = S.make_cases(N, seed, misspecified=misspecified)
        for name, (fn, kw) in VARIANTS.items():
            _, m = run(cases, fn, kw)
            for k in KEYS:
                out[name][k].append(m[k])
    return out


def summary(out):
    return {n: {k: (st.mean(v), st.stdev(v)) for k, v in d.items()} for n, d in out.items()}


def md_table(summ, names, keys):
    lines = ["| Metric | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for k in keys:
        cells = []
        for n in names:
            m, s = summ[n][k]
            cells.append(f"${m:,.0f} ± {s:,.0f}" if "cost" in k else f"{m:.3f} ± {s:.3f}")
        lines.append(f"| {k} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def wins(out, a, b, key="total_cost"):
    return sum(x < y for x, y in zip(out[a][key], out[b][key]))


def main():
    matched, mis = collect(False), collect(True)
    sm, ss = summary(matched), summary(mis)
    main_names = list(POLICY_SET)
    md = [f"# Robustness: {len(SEEDS)} seeds ({SEEDS.start}-{SEEDS.stop - 1}) x {N} cases. Mean ± standard deviation.", "",
          "## A. Matched simulator", "", md_table(sm, main_names, KEYS), "",
          "## B. Misspecified simulator (the agent's assumptions are wrong)", "", md_table(ss, main_names, KEYS), "",
          "## C. Design-change re-tests (matched simulator)", "",
          md_table(sm, ["P3 value of info", "P3b VOI + stakes", "P3b without Other"], KEYS), "",
          f"- DC1: P3b had lower total cost than P3 in {wins(matched, 'P3b VOI + stakes', 'P3 value of info')} of {len(SEEDS)} seeds.",
          f"- DC2: P3b WITH the residual Other state had lower total cost than without it in {wins(matched, 'P3b VOI + stakes', 'P3b without Other')} of {len(SEEDS)} seeds.",
          f"- Misspecified world: P3c beat P2 in {wins(mis, 'P3c + guard 0.7', 'P2 threshold')} of {len(SEEDS)} seeds; matched world: P3c beat P2 in {wins(matched, 'P3c + guard 0.7', 'P2 threshold')} of {len(SEEDS)}.",
          f"- Misspecified world: P3b beat P2 in {wins(mis, 'P3b VOI + stakes', 'P2 threshold')} of {len(SEEDS)} seeds; "
          f"wrong Limits rose from {sm['P3b VOI + stakes']['wrong_limits'][0]:.2f} to {ss['P3b VOI + stakes']['wrong_limits'][0]:.2f} per 500 cases, "
          f"ECE from {sm['P3b VOI + stakes']['ece'][0]:.3f} to {ss['P3b VOI + stakes']['ece'][0]:.3f}."]
    (RESULTS / "robustness.md").write_text("\n".join(md) + "\n")
    dump("robustness.json", {"matched": matched, "misspecified": mis})
    print("\n".join(md))


if __name__ == "__main__":
    main()
