"""
run_failures.py - Collect every wrong decision of P3 (before the design changes) on the
main 500 cases, with the evidence it used and the evidence it never bought, ranked by
how much extra it cost. Then re-run the same case with P3b and P3c (after the changes).
Output: results/failures_raw.md (input for results/failure-analysis.md)
"""
from collections import Counter

from common import E, M, N, P, RESULTS, S, SEED

AGENTS = {"P3": P.Agent(), "P3b": P.Agent(scaled_costs=True), "P3c": P.Agent(scaled_costs=True, limit_guard=0.7)}


def main():
    cases = S.make_cases(N, SEED)
    rows = []
    for c in cases:
        d = P.p3(AGENTS["P3"], c)
        best = E.best_true_action(c)
        if d["action"] == best:
            continue
        dc, ic, dl = E.true_cost(c, d["action"], d["checks"])
        bc, _, _ = E.true_cost(c, best, [])
        after = {k: P.p3(a, c)["action"] for k, a in AGENTS.items() if k != "P3"}
        rows.append((dc + ic + dl - bc, c, d, best, after))
    rows.sort(key=lambda r: -r[0])
    kinds = Counter((r[1]["true_state"], r[2]["action"]) for r in rows)
    L = [f"# Wrong decisions of P3 on the main {N} cases (seed {SEED})", "",
         f"{len(rows)} wrong decisions. By (true state, action): " + ", ".join(f"{k[0]}->{k[1]}: {v}" for k, v in kinds.most_common()), "",
         "Top 15 by extra cost:", ""]
    for extra, c, d, best, after in rows[:15]:
        unseen = [e for e in M.PAID if e not in d["checks"]]
        L += [f"## {c['case_id']}: true {c['true_state']}, ${c['amount']:,.2f}/day, P3 chose {d['action']} (best: {best}), extra cost ${extra:,.0f}",
              f"- Free evidence: " + ", ".join(f"{e}={c[e]}" for e in M.FREE),
              f"- Paid checks bought: " + (", ".join(f"{e}={c[e]}" for e in d["checks"]) or "none") + f" (stop: {d.get('stop')})",
              f"- Never bought: " + ", ".join(f"{e}={c[e]}" for e in unseen),
              f"- Final belief: " + ", ".join(f"{s} {d['belief'][s]:.3f}" for s in M.STATES),
              f"- After design changes: P3b -> {after['P3b']}, P3c -> {after['P3c']}", ""]
    (RESULTS / "failures_raw.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
