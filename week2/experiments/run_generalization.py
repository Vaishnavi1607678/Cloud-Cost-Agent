"""
run_generalization.py - Brief Section 17: what happens when the world changes?

Part 1: change one variable at a time (P0, P2, P3b; 20 seeds x 500 cases):
   (a) cost of a missed problem x100
   (b) every paid check costs x10
   (c) historical data unreliable: the world moved from a STARTUP account to an
       ENTERPRISE account, but the agent still uses its startup priors/likelihoods.
       Compared with an agent that was re-fitted to the enterprise world.
Part 2: Jensen-Shannon divergence alarm. Can the agent NOTICE the move from startup to
       enterprise only from what it observes (the free evidence), before any labels arrive?

Enterprise world (HYPOTHETICAL): more planned jobs and more attacks (bigger target),
tagging is enforced by policy (99% of normal resources tagged), and many automation roles
the agent does not recognise (only 75% of normal launchers 'known').
Output: results/generalization.md
"""
import copy
import random
import statistics as st
from collections import Counter
from itertools import product

from common import M, N, P, RESULTS, S, run
from run_robustness import SEEDS

ENT_PRIOR = {"Normal": 0.68, "Planned": 0.15, "Waste": 0.07, "Compromise": 0.06, "Other": 0.04}
ENT_LIK = copy.deepcopy(M.EVIDENCE)
ENT_LIK["owner_tag"]["lik"]["Normal"] = [0.99, 0.01]
ENT_LIK["owner_tag"]["lik"]["Planned"] = [0.97, 0.03]
ENT_LIK["launcher"]["lik"]["Normal"] = [0.75, 0.25]
ENT_LIK["launcher"]["lik"]["Planned"] = [0.80, 0.20]

POL = {"P0 baseline": (P.p0, {}), "P2 threshold": (P.p2, {}), "P3b VOI + stakes": (P.p3, {"scaled_costs": True})}
KEYS = ["total_cost", "info_cost", "questions_per_case", "human_review_rate", "missed_compromises", "wrong_limits"]


def avg(scenario):
    agent_extra, score_kw, case_kw = scenario
    res = {}
    for name, (fn, kw) in POL.items():
        acc = {k: [] for k in KEYS}
        for seed in SEEDS:
            cases = S.make_cases(N, seed, **case_kw)
            _, m = run(cases, fn, {**kw, **agent_extra}, **score_kw)
            for k in KEYS:
                acc[k].append(m[k])
        res[name] = {k: st.mean(v) for k, v in acc.items()}
    return res


def jsd_alarm(lines):
    """Distribution of the 24 free-evidence patterns, window by window."""
    patterns = list(product(*[M.EVIDENCE[e]["outcomes"] for e in M.FREE]))

    def dist(cases):
        c = Counter(tuple(x[e] for e in M.FREE) for x in cases)
        tot = len(cases) + len(patterns)          # add-one smoothing
        return {p: (c[p] + 1) / tot for p in patterns}

    ref = dist(S.make_cases(5000, 7))
    lines += ["", "## Part 2: Jensen-Shannon divergence alarm", "",
              "Can the agent notice the move from startup to enterprise from the free evidence alone, before any labels arrive? "
              "Reference: 5,000 startup cases. For each window size, the alarm level is the 99th percentile of JSD between "
              "100 startup windows and the reference (about 1 false alarm per 100 windows). Detection rate = share of 100 "
              "enterprise windows above the alarm level.", "",
              "| Window size (cases) | Alarm level (bits) | Mean JSD, startup | Mean JSD, enterprise | False-alarm rate | Detection rate |",
              "|---|---|---|---|---|---|"]
    for size in (100, 200, 500, 1000):
        null = [M.jsd(dist(S.make_cases(size, 10000 + i)), ref) for i in range(100)]
        alarm = sorted(null)[98]
        shifted = [M.jsd(dist(S.make_cases(size, 20000 + i, prior=ENT_PRIOR, lik=ENT_LIK)), ref) for i in range(100)]
        fa = sum(j > alarm for j in null) / len(null)
        det = sum(j > alarm for j in shifted) / len(shifted)
        lines.append(f"| {size} | {alarm:.4f} | {st.mean(null):.4f} | {st.mean(shifted):.4f} | {fa:.2f} | {det:.2f} |")
    lines.append("\nSmall windows are mostly noise: the shift only becomes reliably visible with enough cases. "
                 "Which window size is enough is the honest answer to 'how would you even notice?'.")


def main():
    base = avg(({}, {}, {}))
    scen = {
        "(a) missed-problem cost x100": ({"fn_mult": 100}, {"fn_mult": 100}, {}),
        "(b) paid checks cost x10": ({"price_mult": 10}, {"price_mult": 10}, {}),
        "(c) enterprise world, startup model": ({}, {}, {"prior": ENT_PRIOR, "lik": ENT_LIK}),
        "(c') enterprise world, re-fitted model": ({"prior": ENT_PRIOR, "lik": ENT_LIK}, {}, {"prior": ENT_PRIOR, "lik": ENT_LIK}),
    }
    lines = [f"# Generalization ({len(SEEDS)} seeds x {N} cases, mean)", "",
             "## Part 1: change one variable at a time", "",
             "| Scenario | Policy | Total cost | Info cost | Questions/case | Human review | Missed compromises | Wrong Limits |",
             "|---|---|---|---|---|---|---|---|"]

    def add(name, res):
        for p, m in res.items():
            lines.append(f"| {name} | {p} | ${m['total_cost']:,.0f} | ${m['info_cost']:,.0f} | {m['questions_per_case']:.3f} | "
                         f"{m['human_review_rate']:.3f} | {m['missed_compromises']:.2f} | {m['wrong_limits']:.2f} |")
    add("baseline world", base)
    for name, sc in scen.items():
        add(name, avg(sc))
    fp, fn100 = 50.0, 5000 * 100 - 600
    lines += ["", f"Threshold check for (a): Ignore/Report break-even P(Compromise) falls from 0.0112 to "
              f"50 / (50 + {fn100:,.0f}) = {fp / (fp + fn100):.6f}."]
    jsd_alarm(lines)
    (RESULTS / "generalization.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
