"""
model.py - Week 2 probabilistic model of the cloud cost agent.

Same problem as Week 1:
  The agent observes a daily AWS cost line item and its 7-day history. It must
  ignore, report (send to a human), or limit the cost, because the cause is hidden.

What is new in Week 2 (brief Section 4):
  * a residual hidden state "Other" (price change, expired discount, billing correction)
  * the agent CHOOSES which evidence to buy, and each check has a price and a delay
  * information measures: entropy, information gain, KL and Jensen-Shannon divergence
  * value of information decides whether a check is worth buying

ALL probabilities and costs here are HYPOTHETICAL (my judgement) unless marked
"measured". Where each number came from is written next to it.
"""
from math import log2

MODEL_VERSION = "w2-model-1.0"

STATES = ["Normal", "Planned", "Waste", "Compromise", "Other"]
ACTIONS = ["Ignore", "Report", "Limit"]

# ------------------------------------------------------------------ priors
# Hypothetical. Origin: Week 1 prior (80/8/8/4), with 4 points moved to the new
# residual state "Other" (2 from Normal, 1 from Waste, 1 from Compromise), because
# Week 1 review Q6 and failure F6 showed price changes were being mistaken for spikes.
PRIOR = {"Normal": 0.78, "Planned": 0.08, "Waste": 0.07, "Compromise": 0.03, "Other": 0.04}

# ------------------------------------------------------------------ evidence
# Each evidence source: outcomes, likelihood table P(outcome | state),
# price in US$, time in hours, and whether it is free (read from the bill/API).
#
# Likelihood origins:
#   spike/Normal  : MEASURED from the Week 1 billing data (115 unmodified service-days:
#                   67.0% low, 20.9% med, 12.2% high; Week 1 decision record Part 4)
#   everything else: HYPOTHETICAL, my judgement (to be checked with practitioners)
EVIDENCE = {
    # --- free: read from the billing row itself -----------------------------
    "spike": {   # today's cost / 7-day median: low <1.5x, med 1.5-3x, high >=3x
        "outcomes": ["low", "med", "high"],
        "lik": {"Normal": [0.67, 0.21, 0.12], "Planned": [0.10, 0.45, 0.45],
                "Waste": [0.15, 0.55, 0.30], "Compromise": [0.05, 0.20, 0.75],
                "Other": [0.30, 0.50, 0.20]},
        "price": 0.0, "hours": 0.0, "free": True,
        "question": "How big is today's spike compared with the last 7 days?"},
    "price_jump": {   # cost rose but usage did not (price per unit changed)
        "outcomes": ["yes", "no"],
        "lik": {"Normal": [0.10, 0.90], "Planned": [0.05, 0.95], "Waste": [0.05, 0.95],
                "Compromise": [0.05, 0.95], "Other": [0.85, 0.15]},
        "price": 0.0, "hours": 0.0, "free": True,
        "question": "Did the price per unit jump while usage stayed flat?"},
    "region_new": {
        "outcomes": ["new", "seen"],
        "lik": {"Normal": [0.10, 0.90], "Planned": [0.10, 0.90], "Waste": [0.10, 0.90],
                "Compromise": [0.70, 0.30], "Other": [0.02, 0.98]},
        "price": 0.0, "hours": 0.0, "free": True,
        "question": "Is the cost in a region not used in the last 7 days?"},
    # --- nearly free: one API call --------------------------------------------
    "owner_tag": {
        "outcomes": ["tagged", "untagged"],
        "lik": {"Normal": [0.90, 0.10], "Planned": [0.85, 0.15], "Waste": [0.55, 0.45],
                "Compromise": [0.15, 0.85], "Other": [0.90, 0.10]},
        "price": 0.01, "hours": 0.0003, "free": True,
        "question": "Does the resource have an owner/team tag?"},
    # --- paid checks: the agent decides whether to buy these ------------------
    "launcher": {   # CloudTrail: who created/ran the resource
        "outcomes": ["known", "unknown"],
        "lik": {"Normal": [0.95, 0.05], "Planned": [0.95, 0.05], "Waste": [0.85, 0.15],
                "Compromise": [0.30, 0.70], "Other": [0.95, 0.05]},
        # Compromise 0.30 (not 0.20 as in Week 1): stolen keys show a REAL user (Week 1 failure F3)
        "price": 1.0, "hours": 1 / 60, "free": False,
        "question": "Does CloudTrail show a known person or pipeline launched it?"},
    "ticket": {   # change ticket / deploy calendar entry for that day
        "outcomes": ["found", "none"],
        "lik": {"Normal": [0.10, 0.90], "Planned": [0.80, 0.20], "Waste": [0.10, 0.90],
                "Compromise": [0.05, 0.95], "Other": [0.15, 0.85]},
        "price": 5.0, "hours": 5 / 60, "free": False,
        "question": "Is there a change ticket or deployment for this service today?"},
    "ask_owner": {   # message the owning team and wait for an answer
        "outcomes": ["intended", "not_intended"],
        "lik": {"Normal": [0.90, 0.10], "Planned": [0.95, 0.05], "Waste": [0.20, 0.80],
                "Compromise": [0.05, 0.95], "Other": [0.80, 0.20]},
        "price": 40.0, "hours": 2.0, "free": False,
        "question": "Does the owning team confirm this usage was intended?"},
    "forensics": {   # full security investigation
        "outcomes": ["malicious", "clean"],
        "lik": {"Normal": [0.01, 0.99], "Planned": [0.01, 0.99], "Waste": [0.02, 0.98],
                "Compromise": [0.97, 0.03], "Other": [0.01, 0.99]},
        "price": 2000.0, "hours": 48.0, "free": False,
        "question": "Does a full security investigation find malicious activity?"},
}
FREE = [e for e, v in EVIDENCE.items() if v["free"]]
PAID = [e for e, v in EVIDENCE.items() if not v["free"]]

# ------------------------------------------------------------------ costs
# Hypothetical, US$. At a typical line item of A0 dollars/day these equal the Week 1
# cost table (plus the new Other column).
A0 = 60.0   # MEASURED: mean daily line-item cost in the Week 1 data is $60.89
BASE_COST = {
    "Ignore": {"Normal": 0,   "Planned": 0,    "Waste": 400, "Compromise": 5000, "Other": 100},
    "Report": {"Normal": 50,  "Planned": 50,   "Waste": 40,  "Compromise": 600,  "Other": 30},
    "Limit":  {"Normal": 300, "Planned": 1500, "Waste": 60,  "Compromise": 100,  "Other": 300},
}
# How the loss from IGNORING a problem depends on the bill (hypothetical):
#   Waste:      the extra spend runs about 6.7 days before someone notices  -> 6.67 x amount
#   Compromise: $3,200 fixed (key rotation, investigation, data risk)
#               + the attacker's spend runs ~30 days until the monthly bill -> 3200 + 30 x amount
#   Other:      price change overpaid for ~1.7 days                         -> 1.67 x amount
# At amount = A0 = $60 these give $400, $5,000 and $100, the Week 1 values.
SECURITY_FIXED = 3200.0
DAYS_UNNOTICED = {"Waste": 400 / A0, "Compromise": 30.0, "Other": 100 / A0}


def cost_table(amount=A0, scaled=True):
    """Cost of each action in each state.
    scaled=False: the agent assumes every bill is the typical A0 size (P3).
    scaled=True:  losses from ignoring a problem depend on the actual bill
                  (design change P3b, from failure analysis 'wrong cost assumption')."""
    amt = amount if scaled else A0
    t = {a: dict(BASE_COST[a]) for a in ACTIONS}
    t["Ignore"]["Waste"] = DAYS_UNNOTICED["Waste"] * amt
    t["Ignore"]["Compromise"] = SECURITY_FIXED + DAYS_UNNOTICED["Compromise"] * amt
    t["Ignore"]["Other"] = DAYS_UNNOTICED["Other"] * amt
    return t


def hourly_loss(amount=A0, scaled=True):
    """Loss that keeps growing while the agent waits for a check (per hour)."""
    amt = amount if scaled else A0
    return {"Normal": 0.0, "Planned": 0.0, "Waste": amt / 24,
            "Compromise": amt / 24 + SECURITY_FIXED / 72,   # exposure grows over the first 3 days
            "Other": amt / 48}


# ------------------------------------------------------------------ information measures
def entropy(b):
    """Uncertainty of a belief, in bits (log base 2)."""
    return -sum(p * log2(p) for p in b.values() if p > 0)


def normalise(b):
    z = sum(b.values())
    return {s: v / z for s, v in b.items()}


def update(b, ev, outcome, lik=None):
    """Bayes' rule: posterior is proportional to prior x likelihood."""
    lik = lik or EVIDENCE
    i = lik[ev]["outcomes"].index(outcome)
    return normalise({s: b[s] * lik[ev]["lik"][s][i] for s in b})


def outcome_probs(b, ev, lik=None):
    """P(outcome) = sum over states of P(outcome | state) P(state)."""
    lik = lik or EVIDENCE
    outs = lik[ev]["outcomes"]
    return {o: sum(b[s] * lik[ev]["lik"][s][i] for s in b) for i, o in enumerate(outs)}


def conditional_entropy(b, ev, lik=None):
    """Expected uncertainty left after seeing the evidence: H(S | E)."""
    return sum(p * entropy(update(b, ev, o, lik)) for o, p in outcome_probs(b, ev, lik).items() if p > 0)


def info_gain(b, ev, lik=None):
    """Expected information gain = H(S) - H(S | E) = mutual information I(S; E)."""
    return entropy(b) - conditional_entropy(b, ev, lik)


def kl(p, q):
    """KL divergence D(p || q) in bits. Not symmetric."""
    return sum(p[s] * log2(p[s] / q[s]) for s in p if p[s] > 0)


def jsd(p, q):
    """Jensen-Shannon divergence in bits: symmetric, always finite, between 0 and 1."""
    keys = set(p) | set(q)
    p = {k: p.get(k, 0.0) for k in keys}
    q = {k: q.get(k, 0.0) for k in keys}
    m = {k: 0.5 * (p[k] + q[k]) for k in keys}
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


# ------------------------------------------------------------------ decisions
def expected_cost(b, a, costs):
    return sum(b[s] * costs[a][s] for s in b)


def best_action(b, costs):
    ec = {a: expected_cost(b, a, costs) for a in ACTIONS}
    a = min(ec, key=ec.get)
    return a, ec[a], ec


def value_of_information(b, ev, costs, loss_per_hour, lik=None, price_mult=1.0):
    """Net value of buying one check, in US$:
         (best expected cost now)
       - (expected best cost after seeing the result + price + expected delay loss).
    Positive -> worth buying. Also returns whether ANY outcome changes the action."""
    lik = lik or EVIDENCE
    a_now, ec_now, _ = best_action(b, costs)
    after, changes = 0.0, False
    for o, p in outcome_probs(b, ev, lik).items():
        if p <= 0:
            continue
        a_o, ec_o, _ = best_action(update(b, ev, o, lik), costs)
        after += p * ec_o
        changes |= a_o != a_now
    price = lik[ev]["price"] * price_mult
    delay = lik[ev]["hours"] * sum(b[s] * loss_per_hour[s] for s in b)
    gross = ec_now - after
    return {"net": gross - price - delay, "gross": gross, "price": price,
            "delay": delay, "can_change_action": changes}
