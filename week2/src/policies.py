"""
policies.py - The four Week 2 policies (brief Section 18.2) plus design-change variants.

  P0  Baseline           Always Ignore (the most common correct action). No evidence.
  P1  Belief only        Free evidence -> most probable state -> that state's action.
  P2  Threshold          Free evidence -> lowest expected cost (thresholds derived from costs).
                         Report (send to a human) in the uncertain band.
  P3  Value of info      As P2, then buys paid checks one at a time, best information
                         per dollar among checks with positive value of information,
                         and stops by the stop rule.
  P3b P3 + stakes        Design change DC1 (failure FW2-1): costs of ignoring a problem
                         grow with the size of the bill (threshold moves with stakes).
  P3c P3b + guard 0.7    Design change DC3 (failure FW2-5): the agent may only Limit on its
                         own if P(Compromise) >= 0.7; otherwise a human decides.

Decisions never look at case["true_state"].
"""
import model as M

MAP_STATE_TO_ACTION = {"Normal": "Ignore", "Planned": "Ignore", "Waste": "Report",
                       "Compromise": "Limit", "Other": "Report"}
LIMIT_MIN_P_COMPROMISE = 0.5    # human control (from Week 1)
HUMAN_CEILING = 3000.0          # $/day: any automatic Limit on a bill this big goes to a human
MAX_PAID_CHECKS = 4
STOP_MOVE = 0.02                # stop if two checks in a row move the belief less than this


class Agent:
    """What the agent believes about the world (it may be wrong)."""

    def __init__(self, states=None, prior=None, lik=None, scaled_costs=False,
                 fn_mult=1.0, price_mult=1.0, limit_guard=None):
        self.states = states or list(M.STATES)
        p = prior or M.PRIOR
        self.prior = M.normalise({s: p[s] for s in self.states})
        base = lik or M.EVIDENCE
        # keep only the states this agent knows about
        self.lik = {e: {**v, "lik": {s: v["lik"][s] for s in self.states}} for e, v in base.items()}
        self.scaled, self.fn_mult, self.price_mult = scaled_costs, fn_mult, price_mult
        self.limit_guard = limit_guard

    def costs(self, amount):
        t = M.cost_table(amount if self.scaled else M.A0, scaled=self.scaled)
        for s in ("Waste", "Compromise", "Other"):
            t["Ignore"][s] *= self.fn_mult
        return {a: {s: t[a][s] for s in self.states} for a in t}

    def hourly(self, amount):
        h = M.hourly_loss(amount if self.scaled else M.A0, scaled=self.scaled)
        return {s: h[s] * self.fn_mult for s in self.states}


def _free_belief(agent, case):
    b = dict(agent.prior)
    for ev in M.FREE:
        b = M.update(b, ev, case[ev], agent.lik)
    return b


def _guard(agent, action, b, amount):
    g = agent.limit_guard if agent.limit_guard is not None else LIMIT_MIN_P_COMPROMISE
    if action == "Limit" and (b.get("Compromise", 0) < g or amount > HUMAN_CEILING):
        return "Report", True
    return action, False


def p0(agent, case):
    return {"action": "Ignore", "checks": [], "belief": dict(agent.prior), "trail": []}


def p1(agent, case):
    b = _free_belief(agent, case)
    s = max(b, key=b.get)
    return {"action": MAP_STATE_TO_ACTION[s], "checks": [], "belief": b, "trail": []}


def p2(agent, case):
    b = _free_belief(agent, case)
    a, _, _ = M.best_action(b, agent.costs(case["amount"]))
    a, guarded = _guard(agent, a, b, case["amount"])
    return {"action": a, "checks": [], "belief": b, "trail": [], "guarded": guarded}


def p3(agent, case):
    b = _free_belief(agent, case)
    costs, hourly = agent.costs(case["amount"]), agent.hourly(case["amount"])
    checks, trail, small_moves, stop = [], [], 0, "no paid check has positive value"
    while len(checks) < MAX_PAID_CHECKS:
        cands = []
        for ev in M.PAID:
            if ev in checks:
                continue
            v = M.value_of_information(b, ev, costs, hourly, agent.lik, agent.price_mult)
            if v["net"] > 0:
                ig = M.info_gain(b, ev, agent.lik)
                spend = v["price"] + v["delay"] + 1e-9
                cands.append((ig / spend, ev, v, ig))
        if not cands:
            stop = "no paid check has positive value" if not checks else "remaining checks not worth their cost"
            break
        _, ev, v, ig = max(cands)
        before = b
        b = M.update(b, ev, case[ev], agent.lik)
        checks.append(ev)
        move = 0.5 * sum(abs(b[s] - before[s]) for s in b)
        trail.append({"check": ev, "result": case[ev], "info_gain_bits": ig, "voi": v["net"],
                      "entropy_after": M.entropy(b), "moved": move})
        small_moves = small_moves + 1 if move < STOP_MOVE else 0
        if small_moves >= 2:
            stop = "evidence stopped moving the belief"
            break
    else:
        stop = "check limit reached"
    a, _, _ = M.best_action(b, costs)
    a, guarded = _guard(agent, a, b, case["amount"])
    return {"action": a, "checks": checks, "belief": b, "trail": trail, "guarded": guarded, "stop": stop}


POLICIES = {"P0": p0, "P1": p1, "P2": p2, "P3": p3}
