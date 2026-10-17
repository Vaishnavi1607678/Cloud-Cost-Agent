"""
run_guard.py - Design change DC3, from failure FW2-5 ('untagged normal work looks like an attack').
Should the agent need more certainty before it Limits on its own?
Tests the human-control guard P(Compromise) >= g for g in 0.5, 0.7, 0.9, on the matched and
the misspecified simulator (20 seeds x 500 cases, same seeds as run_robustness.py).
Output: results/guard.md
"""
import statistics as st

from common import N, RESULTS, S, P, run
from run_robustness import SEEDS

GUARDS = [0.5, 0.7, 0.9]
KEYS = ["total_cost", "wrong_limits", "missed_compromises", "human_review_rate"]


def main():
    lines = [f"# DC3: Limit guard threshold (P3b, {len(SEEDS)} seeds x {N} cases, mean)", "",
             "| Simulator | Guard P(Compromise) >= | Total cost | Wrong Limits | Missed compromises | Human review |",
             "|---|---|---|---|---|---|"]
    for mis in (False, True):
        for g in GUARDS:
            acc = {k: [] for k in KEYS}
            for seed in SEEDS:
                _, m = run(S.make_cases(N, seed, misspecified=mis), P.p3, {"scaled_costs": True, "limit_guard": g})
                for k in KEYS:
                    acc[k].append(m[k])
            mean = {k: st.mean(v) for k, v in acc.items()}
            lines.append(f"| {'misspecified' if mis else 'matched'} | {g} | ${mean['total_cost']:,.0f} | "
                         f"{mean['wrong_limits']:.2f} | {mean['missed_compromises']:.2f} | {mean['human_review_rate']:.3f} |")
    (RESULTS / "guard.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
