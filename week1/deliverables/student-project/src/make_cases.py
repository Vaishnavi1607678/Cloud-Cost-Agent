"""
make_cases.py - Build 40 labeled test cases from the mock AWS billing CSV.

How it works (plain words):
  1. Pick a service and a day. Take the 7 days before it as "history".
  2. Take the real cost row for that day as "today".
  3. Leave it alone (Normal), or change it to look like one of 3 problems:
       Planned  - a planned batch job: usage and cost both go up
       Waste    - a forgotten resource / retry loop: usage and cost go up a bit
       Compromise - stolen keys: big jump, often in a region never used before
  4. Add "investigation evidence" (owner tag, who launched it, change ticket).
     The agent only sees this evidence if it chooses to Investigate.

The agent-visible cases go to data/cases.csv.
The true answers go to data/labels.csv (the agent never reads this file).

IMPORTANT LIMITATION: the problem patterns below are my assumptions,
not real incident data. They must be checked with practitioners.
"""
import csv
import random
from pathlib import Path

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "aws_billing_data_mock.csv"

# How many cases of each true state (total 40)
COUNTS = {"Normal": 14, "Planned": 10, "Waste": 9, "Compromise": 7}

# Regions that never appear in the mock data (used for some compromise cases)
UNUSED_REGIONS = ["sa-east-1", "ap-northeast-1", "af-south-1", "me-south-1"]

# Chance that each investigation clue is TRUE, per hidden state.
#   owner_tag:      the resource has a team/owner tag
#   known_launcher: CloudTrail shows a known team member or pipeline launched it
#   change_ticket:  there is a planned change / deployment ticket for that day
EVIDENCE_RATES = {
    "Normal":     {"owner_tag": 0.95, "known_launcher": 0.95, "change_ticket": 0.10},
    "Planned":    {"owner_tag": 0.90, "known_launcher": 0.95, "change_ticket": 0.80},
    "Waste":      {"owner_tag": 0.55, "known_launcher": 0.85, "change_ticket": 0.10},
    "Compromise": {"owner_tag": 0.10, "known_launcher": 0.15, "change_ticket": 0.05},
}


def load_rows():
    with open(RAW, newline="") as f:
        rows = list(csv.DictReader(f))
    by_service = {}
    for r in rows:
        r["UsageAmount"] = float(r["UsageAmount"])
        r["Cost"] = float(r["Cost"])
        by_service.setdefault(r["Service"], []).append(r)
    for s in by_service:
        by_service[s].sort(key=lambda r: r["Date"])
    return by_service


def make_case(rng, by_service, state, case_id):
    # Compromise usually hits compute (EC2 / Lambda); other states any service
    services = ["EC2", "Lambda"] if state == "Compromise" else list(by_service)
    service = rng.choice(services)
    series = by_service[service]
    day = rng.randrange(7, len(series))          # need 7 days of history
    history = series[day - 7:day]
    today = dict(series[day])

    usage, cost, region = today["UsageAmount"], today["Cost"], today["Region"]

    if state == "Planned":
        m = rng.uniform(2.0, 5.0)
        usage, cost = usage * m, cost * m
    elif state == "Waste":
        m = rng.uniform(1.5, 3.5)
        usage, cost = usage * m, cost * m
    elif state == "Compromise":
        m = rng.uniform(3.0, 10.0)
        usage, cost = usage * m, cost * m
        if rng.random() < 0.7:
            region = rng.choice(UNUSED_REGIONS)

    clues = {k: int(rng.random() < p) for k, p in EVIDENCE_RATES[state].items()}

    case = {
        "case_id": case_id,
        "date": today["Date"],
        "service": service,
        "region": region,
        "usage_type": today["UsageType"],
        "usage": round(usage, 2),
        "cost": round(cost, 2),
        "hist_costs": ";".join(f"{h['Cost']:.2f}" for h in history),
        "hist_usage": ";".join(f"{h['UsageAmount']:.2f}" for h in history),
        "hist_regions": ";".join(h["Region"] for h in history),
        # investigation evidence (hidden until the agent pays to investigate)
        **clues,
    }
    return case


def build(seed):
    """Return (cases, labels) in memory for one random seed."""
    rng = random.Random(seed)
    by_service = load_rows()
    states = [s for s, n in COUNTS.items() for _ in range(n)]
    rng.shuffle(states)                         # mix the order
    cases, labels = [], []
    for i, state in enumerate(states, start=1):
        cid = f"C{i:02d}"
        cases.append(make_case(rng, by_service, state, cid))
        labels.append({"case_id": cid, "true_state": state})
    return cases, labels


def main(seed=SEED, tag=""):
    """tag="" writes cases.csv/labels.csv; tag="holdout" writes cases_holdout.csv etc."""
    suffix = f"_{tag}" if tag else ""
    cases_path = ROOT / "data" / f"cases{suffix}.csv"
    labels_path = ROOT / "data" / f"labels{suffix}.csv"
    cases, labels = build(seed)

    for path, data in [(cases_path, cases), (labels_path, labels)]:
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)
    print(f"Wrote {len(cases)} cases to {cases_path.name} and labels to {labels_path.name} (seed {seed})")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--tag", default="", help='e.g. "holdout" -> data/cases_holdout.csv')
    args = ap.parse_args()
    main(args.seed, args.tag)
