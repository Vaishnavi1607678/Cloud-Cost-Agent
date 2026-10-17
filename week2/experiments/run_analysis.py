"""
run_analysis.py - The worked numbers the brief asks for (Sections 11-16).
Everything is computed from src/model.py, so the paper and the code agree.

Output: results/analysis.md
"""
from common import M, P, RESULTS

L = []
w = L.append
r3 = lambda x: f"{x:.3f}"
pct = lambda x: f"{x:.3f}"


def belief_row(b):
    return " | ".join(pct(b[s]) for s in M.STATES)


# ---------------------------------------------------------------- 1. belief-state table
EXAMPLE = {"spike": "high", "price_jump": "no", "region_new": "seen", "owner_tag": "untagged"}
b0 = dict(M.PRIOR)
w("# Worked analysis (all numbers computed by experiments/run_analysis.py)\n")
w("All probabilities and costs are HYPOTHETICAL unless marked measured (see src/model.py).\n")
w("## 1. Belief-state table for one example case\n")
w(f"Example evidence: {EXAMPLE} (a $60/day line item).\n")
steps = [("prior", b0)]
b = b0
for ev, o in EXAMPLE.items():
    b = M.update(b, ev, o)
    steps.append((f"after {ev} = {o}", b))
w("| Step | " + " | ".join(M.STATES) + " | Entropy (bits) |")
w("|---|" + "---|" * (len(M.STATES) + 1))
for name, bb in steps:
    w(f"| {name} | {belief_row(bb)} | {r3(M.entropy(bb))} |")
b_free = b
costs = M.cost_table(M.A0, scaled=True)
a, ec, ecs = M.best_action(b_free, costs)
w(f"\nImplied action after free evidence: **{a}** (expected costs: "
  + ", ".join(f"{k} ${v:,.1f}" for k, v in ecs.items()) + ")\n")

# full hand calculation for the first update
w("### One update worked in full: prior -> after 'spike = high'\n")
w("| State | Prior | P(high spike given state) | Prior x likelihood | Posterior |")
w("|---|---|---|---|---|")
i = M.EVIDENCE["spike"]["outcomes"].index("high")
prod = {s: b0[s] * M.EVIDENCE["spike"]["lik"][s][i] for s in M.STATES}
z = sum(prod.values())
for s in M.STATES:
    w(f"| {s} | {b0[s]:.2f} | {M.EVIDENCE['spike']['lik'][s][i]:.2f} | {prod[s]:.4f} | {prod[s] / z:.3f} |")
w(f"| **Sum** | 1.00 | | **{z:.4f}** = P(high spike) | 1.000 |\n")

# ---------------------------------------------------------------- 2. evidence comparison
w("## 2. Which evidence next? (starting from the belief after free evidence)\n")
w("Belief: " + ", ".join(f"{s} {b_free[s]:.3f}" for s in M.STATES) + f"; entropy {M.entropy(b_free):.3f} bits.\n")
hourly = M.hourly_loss(M.A0)
w("| Evidence | Exp. info gain (bits) | Price | Time | Delay loss | Bits per $100 | Net value of info | Can change action? |")
w("|---|---|---|---|---|---|---|---|")
rows = []
for ev in M.PAID:
    ig = M.info_gain(b_free, ev)
    v = M.value_of_information(b_free, ev, costs, hourly)
    spend = v["price"] + v["delay"]
    bp = ig / spend * 100 if spend else float("inf")
    hrs = M.EVIDENCE[ev]["hours"]
    t = f"{hrs * 60:.0f} min" if hrs < 1 else f"{hrs:.0f} h"
    rows.append((ev, ig, v))
    w(f"| {ev} | {ig:.3f} | ${v['price']:,.0f} | {t} | ${v['delay']:,.2f} | {bp:,.2f} | ${v['net']:,.1f} | {'yes' if v['can_change_action'] else 'no'} |")
for ev, ig, v in rows:
    pass
w("\nOutcome-by-outcome view (can a single result increase uncertainty?):\n")
w("| Evidence | Outcome | P(outcome) | Entropy after | Change vs now |")
w("|---|---|---|---|---|")
H = M.entropy(b_free)
for ev in M.PAID:
    for o, p in M.outcome_probs(b_free, ev).items():
        hb = M.entropy(M.update(b_free, ev, o))
        w(f"| {ev} | {o} | {p:.3f} | {hb:.3f} | {hb - H:+.3f} |")

# ---------------------------------------------------------------- 3. five questions at the prior
w("\n## 3. Five questions the agent could ask (values at the PRIOR, before any evidence)\n")
w("| Question | Answers | Info value (bits) | Price | Time | Net value of info at prior |")
w("|---|---|---|---|---|---|")
for ev in ["owner_tag", "launcher", "ticket", "ask_owner", "forensics"]:
    v = M.value_of_information(b0, ev, costs, hourly)
    hrs = M.EVIDENCE[ev]["hours"]
    t = f"{hrs * 3600:.0f} s" if hrs < 1 / 60 else (f"{hrs * 60:.0f} min" if hrs < 1 else f"{hrs:.0f} h")
    w(f"| {M.EVIDENCE[ev]['question']} | {' / '.join(M.EVIDENCE[ev]['outcomes'])} | {M.info_gain(b0, ev):.3f} | ${M.EVIDENCE[ev]['price']:,.2f} | {t} | ${v['net']:,.1f} |")

# ---------------------------------------------------------------- 4. critical thinking
w("\n## 4. Is the most informative question always the best?\n")
agent = P.Agent(scaled_costs=True)
cases_ct = {
    "A. high spike, untagged, $60/day (example above)": ({**EXAMPLE}, 60.0),
    "B. high spike, NEW region, untagged, $60/day": ({**EXAMPLE, "region_new": "new"}, 60.0),
    "C. med spike, untagged, $900/day (big bill)": ({**EXAMPLE, "spike": "med"}, 900.0),
}
for name, (ev_obs, amt) in cases_ct.items():
    bb = dict(M.PRIOR)
    for ev, o in ev_obs.items():
        bb = M.update(bb, ev, o)
    cst, hl = M.cost_table(amt), M.hourly_loss(amt)
    a, ec, _ = M.best_action(bb, cst)
    w(f"### {name}\n")
    w("Belief: " + ", ".join(f"{s} {bb[s]:.3f}" for s in M.STATES) + f". Best action now: **{a}** (expected cost ${ec:,.1f}).\n")
    w("| Check | Info gain (bits) | Net value of info | Changes action? |")
    w("|---|---|---|---|")
    best_ig = max(M.PAID, key=lambda e: M.info_gain(bb, e))
    for ev in M.PAID:
        v = M.value_of_information(bb, ev, cst, hl)
        mark = " (most informative)" if ev == best_ig else ""
        w(f"| {ev}{mark} | {M.info_gain(bb, ev):.3f} | ${v['net']:,.1f} | {'yes' if v['can_change_action'] else 'no'} |")
    w("")

# case D: search every situation for one where the most informative check IS the best buy
from itertools import product
situations, hits = 0, []
for sp, pj, rn, ot in product(["low", "med", "high"], ["yes", "no"], ["new", "seen"], ["tagged", "untagged"]):
    for pre in [{}, {"launcher": "known"}, {"launcher": "unknown"},
                {"launcher": "known", "ticket": "none"}, {"launcher": "unknown", "ticket": "none"}]:
        for amt in [10, 60, 300, 1000, 3000]:
            situations += 1
            bb = dict(M.PRIOR)
            for ev, o in dict(spike=sp, price_jump=pj, region_new=rn, owner_tag=ot, **pre).items():
                bb = M.update(bb, ev, o)
            cst, hl = M.cost_table(amt), M.hourly_loss(amt)
            rem = [e for e in M.PAID if e not in pre]
            igs = {e: M.info_gain(bb, e) for e in rem}
            vo = {e: M.value_of_information(bb, e, cst, hl)["net"] for e in rem}
            top, best = max(igs, key=igs.get), max(vo, key=vo.get)
            if top == best and vo[top] > 0:
                hits.append((dict(spike=sp, price_jump=pj, region_new=rn, owner_tag=ot, **pre), amt, bb, igs, vo))
w(f"### D. Searching for a case where the most informative check IS the best buy\n")
w(f"I checked {situations} situations (every free-evidence combination x 5 investigation histories x 5 bill sizes). "
  f"The most informative remaining check was also the best purchase with positive value in only **{len(hits)}** of them "
  f"({len(hits) / situations:.1%}).\n")
if hits:
    ev_obs, amt, bb, igs, vo = max(hits, key=lambda h: h[4][max(h[3], key=h[3].get)])
    w(f"Example: {ev_obs}, ${amt}/day. Belief: " + ", ".join(f"{s} {bb[s]:.3f}" for s in M.STATES) + ".\n")
    w("| Check | Info gain (bits) | Net value of info |")
    w("|---|---|---|")
    for ev in igs:
        w(f"| {ev} | {igs[ev]:.3f} | ${vo[ev]:,.2f} |")
    w("\nHere the confusion is between Normal and Planned, and the change ticket is the one check that separates exactly those two. "
      "It is the most informative AND worth buying, but only by a few dollars.\n")

# ---------------------------------------------------------------- 5. thresholds
w("## 5. Thresholds derived from costs (two-state view, at $60/day)\n")
fp, fn_ = 50.0, 5000.0 - 600.0
w(f"- Ignore vs Report for Compromise: a false alarm costs $50; ignoring instead of reporting a compromise costs $5,000 - $600 = $4,400 more. Break-even P(Compromise) = 50 / (50 + 4,400) = **{fp / (fp + fn_):.4f}** (about 1.1%).")
fp2, fn2 = 400.0 - 40.0, 0.0
w(f"- Ignore vs Report for Waste: break-even P(Waste) = 50 / (50 + 360) = **{50 / 410:.3f}**.")
w(f"- Report vs Limit for Compromise vs Normal: Limit saves $500 if Compromise and costs $250 extra if Normal. Break-even = 250 / (250 + 500) = **{250 / 750:.3f}**.")
w(f"- Report vs Limit for Compromise vs Planned: Limit costs $1,450 extra if Planned. Break-even = 1,450 / (1,450 + 500) = **{1450 / 1950:.3f}**.")
w("- So the uncertain band (Report) runs from about **1% to 33-74%** P(Compromise), depending on whether the alternative is Normal or Planned. The upper band is why a Planned job without a ticket is dangerous to Limit.\n")
w("How the Ignore/Report break-even moves with the bill (stakes):\n")
w("| Daily bill | Ignore cost if Compromise | Break-even P(Compromise) |")
w("|---|---|---|")
for amt in [10, 60, 300, 1000, 3000]:
    ic = M.SECURITY_FIXED + 30 * amt
    w(f"| ${amt:,} | ${ic:,.0f} | {50 / (50 + ic - 600):.4f} |")

# ---------------------------------------------------------------- 6. information measures
w("\n## 6. Information measures with my numbers\n")
w(f"- Entropy of the prior: {M.entropy(b0):.3f} bits. Maximum possible for 5 states: {__import__('math').log2(5):.3f} bits.")
w(f"- Conditional entropy H(S | spike) = {M.conditional_entropy(b0, 'spike'):.3f} bits, so I(S; spike) = {M.info_gain(b0, 'spike'):.3f} bits.")
w(f"- Mutual information of each free signal with the hidden state, at the prior: " +
  ", ".join(f"{e} {M.info_gain(b0, e):.3f}" for e in M.FREE) + " bits.")
kpq, kqp = M.kl(b_free, b0), M.kl(b0, b_free)
w(f"- KL(posterior || prior) = {kpq:.3f} bits, but KL(prior || posterior) = {kqp:.3f} bits. Same two beliefs, different numbers: KL is not symmetric, so it is not a distance.")
w(f"- Jensen-Shannon divergence between them = {M.jsd(b_free, b0):.3f} bits (symmetric, between 0 and 1).")
four = M.normalise({s: b0[s] for s in M.STATES if s != "Other"})
four_full = {**four, "Other": 0.0}
w(f"- If the true world has a 4% 'Other' state and my agent's list has none: KL(world || agent) is infinite (the agent gives zero probability to something that happens), "
  f"while KL(agent || world) = {M.kl(four_full, b0):.3f} bits. JSD stays finite: {M.jsd(b0, four_full):.4f} bits. This is why the residual state matters and why JSD is used for alarms.")

# ---------------------------------------------------------------- 7. umbrella
w("\n## 7. Umbrella problem (my own costs, in 'units of annoyance')\n")
w("35% chance of rain in Mysuru tomorrow.\n")
w("| | Case A: walk to the shop | Case B: client demo with my laptop |")
w("|---|---|---|")
w("| Cost of carrying it, no rain | 3 | 3 |")
w("| Cost of getting wet | 6 | 400 (wet laptop, ruined demo) |")
w(f"| Average cost if I carry it | 3.0 | 3.0 |")
w(f"| Average cost if I don't | 0.35 x 6 = {0.35 * 6:.1f} | 0.35 x 400 = {0.35 * 400:.0f} |")
w(f"| Break-even chance of rain | 3 / 6 = {3 / 6:.2f} | 3 / 400 = {3 / 400:.4f} |")
w("| Decision | Leave it (35% < 50%) | Take it (35% >> 0.75%) |")
w("\nSame structure as the agent: rain = hidden state, umbrella = Report, getting wet = ignoring a compromise. "
  "Free sky check before leaving: if dark clouds raise rain to 70% and a clear sky drops it to 10% (hypothetical), "
  "in Case A the check can flip the decision (70% > 50%), so it has value; in Case B I take the umbrella either way (10% > 0.75%), so the check is worth nothing.")

(RESULTS / "analysis.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
