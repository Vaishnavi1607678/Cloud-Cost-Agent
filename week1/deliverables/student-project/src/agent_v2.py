"""
agent_v2.py - Version 2 of the cloud cost agent.

Each change comes from a named failure of v1 (see results/failure-analysis.md):

  Change 1  Spike signal uses BOTH cost and usage            <- F2 "Usage spike hidden by price noise" (C06)
            spike ratio = max(cost ratio, usage ratio)
  Change 2  Owner-tag check is automatic and free            <- F1 "Quiet compromise" (C28)
            (a tags API call costs ~nothing, so the agent always reads it).
            "Investigate" now means the paid human check: CloudTrail launcher + change ticket.
  Change 3  Learn from feedback                              <- Section 8 "Feedback" / Section 12 "How does the agent learn?"
            After each decision the true state is revealed; the agent updates its
            likelihood tables with pseudo-counts (Beta / Dirichlet counting).
  Change 4  Human guard on Limit                             <- Section 10 "human control"
            The agent may only Limit by itself if P(Compromise) >= 0.5.
            Otherwise it sends the case to a human (Report).

Not changed on purpose: the prior and the cost table (they need human input
from Reddit/X first), and P(known_launcher | Compromise) (open question, F3).
"""
import statistics
from itertools import product

import agent as v1

POLICY_VERSION = "v2.0"
STATES, ACTIONS, COST = v1.STATES, v1.ACTIONS, v1.COST
PRIOR = dict(v1.PRIOR)
INVESTIGATE_COST = v1.INVESTIGATE_COST
FREE_CLUES = ["owner_tag"]                         # always observed (Change 2)
PAID_CLUES = ["known_launcher", "change_ticket"]   # observed only if Investigate
LIMIT_MIN_P_COMPROMISE = 0.5                       # Change 4
LEARN_STRENGTH = 10                                # how strongly the starting estimates resist new data

# Switches for the ablation study (experiments/run_ablation.py). All True = full v2.
USE_USAGE_RATIO = True     # Change 1
FREE_OWNER_TAG = True      # Change 2
USE_LIMIT_GUARD = True     # Change 4


def observe(case):
    hc = [float(x) for x in case["hist_costs"].split(";")]
    hu = [float(x) for x in case["hist_usage"].split(";")]
    cost_ratio = float(case["cost"]) / statistics.median(hc)
    usage_ratio = float(case["usage"]) / statistics.median(hu)
    ratio = max(cost_ratio, usage_ratio) if USE_USAGE_RATIO else cost_ratio   # Change 1
    spike = "low" if ratio < 1.5 else ("med" if ratio < 3.0 else "high")
    return {"ratio": ratio, "cost_ratio": cost_ratio, "usage_ratio": usage_ratio,
            "spike": spike,
            "region_new": case["region"] not in case["hist_regions"].split(";"),
            "owner_tag": int(case["owner_tag"])}


class Model:
    """Likelihood tables that can learn from feedback (Change 3)."""

    def __init__(self, learn=True):
        self.learn = learn
        L = v1.LIKELIHOOD
        k = LEARN_STRENGTH
        # spike counts: counts[state][level]
        self.spike = {s: {lv: L["spike"][lv][s] * k for lv in ("low", "med", "high")}
                      for s in STATES}
        # binary features: [count_true, count_false] per state
        self.binary = {f: {s: [L[f][s] * k, (1 - L[f][s]) * k] for s in STATES}
                       for f in ["region_new", "owner_tag", "known_launcher", "change_ticket"]}

    def like(self, name, value, state):
        if name == "spike":
            c = self.spike[state]
            return c[value] / sum(c.values())
        t, f = self.binary[name][state]
        p = t / (t + f)
        return p if value else 1 - p

    def update_belief(self, belief, name, value):
        new = {s: belief[s] * self.like(name, value, s) for s in STATES}
        z = sum(new.values())
        return {s: v / z for s, v in new.items()}

    def feedback(self, true_state, obs, paid_clues):
        """Called AFTER the decision, when the true state is revealed."""
        if not self.learn:
            return
        self.spike[true_state][obs["spike"]] += 1
        free = ["region_new"] + (["owner_tag"] if FREE_OWNER_TAG else [])
        for f in free:
            self.binary[f][true_state][0 if obs[f] else 1] += 1
        for f, v in (paid_clues or {}).items():
            self.binary[f][true_state][0 if v else 1] += 1


def expected_cost(b, a):
    return sum(b[s] * COST[a][s] for s in STATES)


def best_action(b):
    costs = {a: expected_cost(b, a) for a in ACTIONS}
    a = min(costs, key=costs.get)
    return a, costs[a]


def guard(action, b):
    """Change 4: only Limit automatically when compromise is likely."""
    if USE_LIMIT_GUARD and action == "Limit" and b["Compromise"] < LIMIT_MIN_P_COMPROMISE:
        return "Report", True
    return action, False


def paid_clues():
    return PAID_CLUES if FREE_OWNER_TAG else ["owner_tag"] + PAID_CLUES


def cost_if_investigate(model, b):
    clues = paid_clues()
    total = INVESTIGATE_COST
    for outcome in product([0, 1], repeat=len(clues)):
        p_out = 0.0
        joint = {}
        for s in STATES:
            p = 1.0
            for f, v in zip(clues, outcome):
                p *= model.like(f, v, s)
            joint[s] = b[s] * p
            p_out += joint[s]
        post = {s: joint[s] / p_out for s in STATES}
        total += p_out * best_action(post)[1]
    return total


def decide(model, case):
    obs = observe(case)
    b = dict(PRIOR)
    b = model.update_belief(b, "spike", obs["spike"])
    b = model.update_belief(b, "region_new", obs["region_new"])
    if FREE_OWNER_TAG:
        b = model.update_belief(b, "owner_tag", obs["owner_tag"])  # free clue (Change 2)
    b_before = dict(b)

    act_now, cost_now = best_action(b)
    investigated, paid = False, None
    if cost_if_investigate(model, b) < cost_now:
        investigated = True
        paid = {f: int(case[f]) for f in paid_clues()}
        for f, v in paid.items():
            b = model.update_belief(b, f, v)
        act_now, cost_now = best_action(b)
    action, guarded = guard(act_now, b)
    return {"action": action, "investigated": investigated, "guarded": guarded,
            "belief_before": b_before, "belief": b, "obs": obs, "paid_clues": paid,
            "expected_cost": cost_now}
