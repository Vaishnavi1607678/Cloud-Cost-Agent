"""
run_feedback.py - Component 11 (feedback) and 12 (belief update), brief Section 10.

The agent learns its prior from feedback after each decision (Dirichlet counts,
starting from its prior with a weight of 100 cases). Three feedback regimes:

  full       every true state is eventually revealed (ideal, unrealistic)
  asymmetric only cases the agent Reported or Limited get investigated, so their
             true state is revealed. Ignored cases produce no complaint and are
             counted as Normal ("no news is good news").
  audit 5%   ignored cases are NOT assumed Normal. A random 5% of them are audited; each
             audited case counts 20 times (1 / 0.05), because it stands for the 19 ignored
             cases that were not audited (inverse-probability weighting). Un-audited
             ignored cases add nothing.

The world is a 'noisy' account where waste is a bit more common than the agent first
assumes (HYPOTHETICAL: Waste 12%, Normal 73%). 5,000 cases, 5 seeds.
Output: results/feedback.md
"""
import random
import statistics as st

from common import M, P, RESULTS, S
import evaluate as E

WORLD = {"Normal": 0.73, "Planned": 0.08, "Waste": 0.12, "Compromise": 0.03, "Other": 0.04}
WEIGHT, N_CASES, SEEDS = 100, 5000, range(5)
AUDIT = 0.05
CHECKPOINTS = [500, 1000, 2000, 3000, 5000]


def run_stream(regime, seed):
    cases = S.make_cases(N_CASES, seed, prior=WORLD)
    rng = random.Random(seed + 99)
    counts = {s: M.PRIOR[s] * WEIGHT for s in M.STATES}
    out, missed_w, missed_c, cost = {}, 0, 0, 0.0
    for i, c in enumerate(cases, 1):
        agent = P.Agent(prior=M.normalise(counts), scaled_costs=True)
        d = P.p2(agent, c)
        dc, ic, dl = E.true_cost(c, d["action"], d["checks"])
        cost += dc + ic + dl
        missed_w += c["true_state"] == "Waste" and d["action"] == "Ignore"
        missed_c += c["true_state"] == "Compromise" and d["action"] == "Ignore"
        # ---- feedback arrives (or not) ----
        if regime == "full" or d["action"] != "Ignore":
            counts[c["true_state"]] += 1
        elif regime == "audit 5%":
            if rng.random() < AUDIT:
                counts[c["true_state"]] += 1 / AUDIT     # inverse-probability weight
        else:
            counts["Normal"] += 1          # no complaint -> assumed fine
        if i in CHECKPOINTS:
            b = M.normalise(counts)
            out[i] = {"p_waste": b["Waste"], "p_comp": b["Compromise"], "kl_world_agent": M.kl(WORLD, b)}
    return out, missed_w, missed_c, cost


def main():
    lines = [f"# Feedback asymmetry: learning the prior from what the agent hears back", "",
             f"World: {WORLD} (hypothetical). Agent starts from {M.PRIOR}. Policy: P2 with stakes. "
             f"{N_CASES} cases x {len(SEEDS)} seeds, mean.", "",
             "| Regime | Cases seen | Learned P(Waste) (true 0.12) | Learned P(Compromise) (true 0.03) | KL(world || learned prior) |",
             "|---|---|---|---|---|"]
    summary = []
    for regime in ("full", "asymmetric", "audit 5%"):
        runs = [run_stream(regime, s) for s in SEEDS]
        for cp in CHECKPOINTS:
            pw = st.mean(r[0][cp]["p_waste"] for r in runs)
            pc = st.mean(r[0][cp]["p_comp"] for r in runs)
            k = st.mean(r[0][cp]["kl_world_agent"] for r in runs)
            lines.append(f"| {regime} | {cp} | {pw:.4f} | {pc:.4f} | {k:.4f} |")
        summary.append((regime, st.mean(r[1] for r in runs), st.mean(r[2] for r in runs), st.mean(r[3] for r in runs)))
    lines += ["", "| Regime | Missed waste (of ~600) | Missed compromises (of ~150) | Total cost |", "|---|---|---|---|"]
    for regime, mw, mc, c in summary:
        lines.append(f"| {regime} | {mw:.1f} | {mc:.1f} | ${c:,.0f} |")
    lines += ["", "Reading: with asymmetric feedback the agent only hears about the problems it already caught, so every "
              "missed problem is silently counted as Normal and the learned prior drifts away from the truth instead of towards it. "
              "Auditing a random 5% of ignored cases, and weighting each audited case by 1/0.05, removes most of that bias. "
              "In this setting the biased prior changes the total cost only a little, because P2 decides mostly from the evidence; "
              "the damage is that the agent's picture of the world is wrong and does not correct itself."]
    (RESULTS / "feedback.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
