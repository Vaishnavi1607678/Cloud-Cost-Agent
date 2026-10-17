"""
simulate.py - Generate simulated cases for the Week 2 experiment.

Brief Section 18.5: draw the true hidden state from the priors, then draw every
evidence outcome from the likelihood tables. The agent never sees the true state.

The daily bill amount is built from a REAL row of the Week 1 billing data
(data/aws_billing_data_mock.csv) multiplied by a factor that matches the
spike level, so big spikes really are big bills.

Two simulators:
  * "matched"     - evidence drawn from the same likelihoods the agent uses.
                    Tests the POLICY given the likelihoods (circular for the likelihoods).
  * "misspecified"- the world differs from the agent's model in two realistic ways:
        1. Stolen keys show a KNOWN launcher 60% of the time (agent assumes 30%).
        2. In Normal/Planned, an untagged resource is usually made by an automation role
           that CloudTrail shows as unknown, so "untagged" and "unknown launcher" come
           together (the agent assumes they are independent).
    This tests what happens when the agent's assumptions are wrong.
"""
import csv
import random
from pathlib import Path

import model as M

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "aws_billing_data_mock.csv"
SPIKE_MULT = {"low": (0.5, 1.5), "med": (1.5, 3.0), "high": (3.0, 10.0)}


def _base_costs():
    with open(RAW, newline="") as f:
        return [float(r["Cost"]) for r in csv.DictReader(f)]


BASE_COSTS = _base_costs()


def _draw(rng, ev, state, lik):
    outs, probs = lik[ev]["outcomes"], lik[ev]["lik"][state]
    return rng.choices(outs, weights=probs)[0]


def make_cases(n, seed, prior=None, lik=None, misspecified=False):
    """Return a list of cases. Each case has 'true_state' (hidden from the agent)
    and one observed outcome for every evidence source."""
    rng = random.Random(seed)
    prior = prior or M.PRIOR
    lik = lik or M.EVIDENCE
    states, weights = list(prior), list(prior.values())
    cases = []
    for i in range(n):
        s = rng.choices(states, weights=weights)[0]
        obs = {ev: _draw(rng, ev, s, lik) for ev in lik}
        if misspecified:
            if s == "Compromise":
                obs["launcher"] = "known" if rng.random() < 0.60 else "unknown"
            if s in ("Normal", "Planned") and obs["owner_tag"] == "untagged":
                obs["launcher"] = "unknown" if rng.random() < 0.70 else "known"
        lo, hi = SPIKE_MULT[obs["spike"]]
        amount = rng.choice(BASE_COSTS) * rng.uniform(lo, hi)
        cases.append({"case_id": f"S{i:04d}", "true_state": s, "amount": round(amount, 2), **obs})
    return cases
