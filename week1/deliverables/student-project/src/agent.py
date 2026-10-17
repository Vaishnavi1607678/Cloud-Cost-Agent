"""
agent.py - The cloud cost agent.

Parts of the agent (Section 8 of the instructions):
  Input        : one cost row + 7 days of history for the same service
  Hidden state : Normal, Planned, Waste, Compromise
  Belief       : probability of each hidden state (always sums to 1)
  Actions      : Ignore, Report, Limit  (+ Investigate = pay to see more evidence)
  Cost         : COST table below, in US dollars (my estimates, to be checked)
  Policy       : see the policy_* functions
  Feedback     : after acting, the true state is revealed and logged

Human reasoning function: "change a belief after new evidence".
The agent uses Bayes' rule:  posterior ∝ prior × likelihood(evidence | state)
"""
import statistics
from itertools import product

POLICY_VERSION = "v1.0"

STATES = ["Normal", "Planned", "Waste", "Compromise"]
ACTIONS = ["Ignore", "Report", "Limit"]

# ---------------------------------------------------------------- beliefs
# Prior: how common each cause is before looking at the evidence.
PRIOR = {"Normal": 0.80, "Planned": 0.08, "Waste": 0.08, "Compromise": 0.04}

# Likelihoods: P(evidence | state). These are MY ESTIMATES, written before
# testing. They are not copied from the case generator.
LIKELIHOOD = {
    # spike = today's cost / median cost of the last 7 days
    "spike": {
        "low":  {"Normal": 0.75, "Planned": 0.10, "Waste": 0.15, "Compromise": 0.05},
        "med":  {"Normal": 0.20, "Planned": 0.45, "Waste": 0.55, "Compromise": 0.20},
        "high": {"Normal": 0.05, "Planned": 0.45, "Waste": 0.30, "Compromise": 0.75},
    },
    # region_new = region not seen in the last 7 days (value = P(new | state))
    "region_new":     {"Normal": 0.15, "Planned": 0.15, "Waste": 0.15, "Compromise": 0.70},
    # Investigation clues (value = P(clue is true | state))
    "owner_tag":      {"Normal": 0.90, "Planned": 0.90, "Waste": 0.60, "Compromise": 0.20},
    "known_launcher": {"Normal": 0.90, "Planned": 0.90, "Waste": 0.80, "Compromise": 0.20},
    "change_ticket":  {"Normal": 0.10, "Planned": 0.70, "Waste": 0.10, "Compromise": 0.10},
}
CLUES = ["owner_tag", "known_launcher", "change_ticket"]

# ---------------------------------------------------------------- costs ($)
# COST[action][state] = what it costs if we take `action` and the truth is `state`.
#   Ignore a Compromise: attackers keep running for days       -> very expensive
#   Limit a Planned job: we break a real production workload   -> outage cost
#   Report anything: an engineer spends time looking           -> small cost
COST = {
    "Ignore": {"Normal": 0,   "Planned": 0,    "Waste": 400, "Compromise": 5000},
    "Report": {"Normal": 50,  "Planned": 50,   "Waste": 40,  "Compromise": 600},
    "Limit":  {"Normal": 300, "Planned": 1500, "Waste": 60,  "Compromise": 100},
}
INVESTIGATE_COST = 25          # engineer / API time to check tags + CloudTrail

# The "correct" action for each true state (cheapest column entry above)
BEST_ACTION = {s: min(ACTIONS, key=lambda a: COST[a][s]) for s in STATES}


# ---------------------------------------------------------------- evidence
def observe(case):
    """Turn a raw case into the evidence the agent can see for free."""
    hist = [float(x) for x in case["hist_costs"].split(";")]
    median = statistics.median(hist)
    ratio = float(case["cost"]) / median if median > 0 else 99.0
    spike = "low" if ratio < 1.5 else ("med" if ratio < 3.0 else "high")
    region_new = case["region"] not in case["hist_regions"].split(";")
    return {"ratio": ratio, "spike": spike, "region_new": region_new}


def normalise(b):
    total = sum(b.values())
    return {s: v / total for s, v in b.items()}


def update(belief, name, value):
    """Bayes' rule for one piece of evidence."""
    new = {}
    for s in STATES:
        if name == "spike":
            like = LIKELIHOOD["spike"][value][s]
        else:
            p_true = LIKELIHOOD[name][s]
            like = p_true if value else 1 - p_true
        new[s] = belief[s] * like
    return normalise(new)


def initial_belief(obs):
    b = dict(PRIOR)
    b = update(b, "spike", obs["spike"])
    b = update(b, "region_new", obs["region_new"])
    return b


def expected_cost(belief, action):
    return sum(belief[s] * COST[action][s] for s in STATES)


def best_by_expected_cost(belief):
    costs = {a: expected_cost(belief, a) for a in ACTIONS}
    a = min(costs, key=costs.get)
    return a, costs[a]


def value_of_investigating(belief):
    """Expected cost if we investigate first, then act on the updated belief.
    We list all 8 possible clue outcomes and weight each by its probability."""
    total = INVESTIGATE_COST
    for outcome in product([0, 1], repeat=len(CLUES)):
        # probability of this outcome under our current belief
        p_outcome = 0.0
        post = {}
        for s in STATES:
            p = 1.0
            for clue, v in zip(CLUES, outcome):
                p *= LIKELIHOOD[clue][s] if v else 1 - LIKELIHOOD[clue][s]
            post[s] = belief[s] * p
            p_outcome += post[s]
        if p_outcome == 0:
            continue
        post = normalise(post)
        total += p_outcome * best_by_expected_cost(post)[1]
    return total


# ---------------------------------------------------------------- policies
def policy_baseline(case):
    """Baseline: classic threshold alert. Report if cost > mean + 2*std."""
    hist = [float(x) for x in case["hist_costs"].split(";")]
    mean, sd = statistics.mean(hist), statistics.stdev(hist)
    z = (float(case["cost"]) - mean) / sd if sd > 0 else 0.0
    action = "Report" if z > 2.0 else "Ignore"
    return {"action": action, "investigated": False, "z": round(z, 2)}


def policy_baseline_usage(case):
    """Stronger baseline (added after preprint review R3): Report if the z-score of
    cost OR of usage is above 2. Same information about usage as agent v2."""
    def z(today, hist):
        hist = [float(x) for x in hist.split(";")]
        mean, sd = statistics.mean(hist), statistics.stdev(hist)
        return (float(today) - mean) / sd if sd > 0 else 0.0
    zc = z(case["cost"], case["hist_costs"])
    zu = z(case["usage"], case["hist_usage"])
    action = "Report" if max(zc, zu) > 2.0 else "Ignore"
    return {"action": action, "investigated": False, "z": round(max(zc, zu), 2)}


MAP_ACTION = {"Normal": "Ignore", "Planned": "Ignore", "Waste": "Report", "Compromise": "Limit"}


def policy_A(case):
    """Policy A: pick the MOST LIKELY state, then do that state's action.
    Ignores how expensive each mistake is."""
    obs = observe(case)
    b = initial_belief(obs)
    state = max(b, key=b.get)
    return {"action": MAP_ACTION[state], "investigated": False, "belief": b, "obs": obs}


def policy_B(case):
    """Policy B: pick the action with the LOWEST EXPECTED COST. No investigation."""
    obs = observe(case)
    b = initial_belief(obs)
    action, ec = best_by_expected_cost(b)
    return {"action": action, "investigated": False, "belief": b, "obs": obs,
            "expected_cost": ec}


def policy_C(case):
    """Policy C: like B, but first asks 'is it worth paying to investigate?'
    If yes, it reads the clues, updates its belief (Bayes), then acts."""
    obs = observe(case)
    b0 = initial_belief(obs)
    act_now, cost_now = best_by_expected_cost(b0)
    cost_if_investigate = value_of_investigating(b0)

    if cost_if_investigate < cost_now:
        b = dict(b0)
        for clue in CLUES:
            b = update(b, clue, int(case[clue]))
        action, ec = best_by_expected_cost(b)
        return {"action": action, "investigated": True, "belief_before": b0,
                "belief": b, "obs": obs, "expected_cost": ec}
    return {"action": act_now, "investigated": False, "belief_before": b0,
            "belief": b0, "obs": obs, "expected_cost": cost_now}


POLICIES = {"Baseline": policy_baseline, "A_most_likely": policy_A,
            "B_expected_cost": policy_B, "C_expected_cost_investigate": policy_C}
