"""
evaluate.py - Score decisions against the hidden truth (only AFTER all decisions).

True cost of one case =
    cost of the final action in the true state (losses scale with the bill size)
  + price of every check bought
  + loss that kept growing while the agent waited for checks (hours x hourly loss)
"""
from math import log2

import model as M

PROBLEM = ("Waste", "Compromise")


def true_cost(case, action, checks, fn_mult=1.0, price_mult=1.0):
    s, amt = case["true_state"], case["amount"]
    t = M.cost_table(amt, scaled=True)
    c = t[action][s] * (fn_mult if action == "Ignore" and s in ("Waste", "Compromise", "Other") else 1.0)
    info = sum(M.EVIDENCE[e]["price"] * price_mult for e in checks)
    delay = sum(M.EVIDENCE[e]["hours"] for e in checks) * M.hourly_loss(amt)[s] * fn_mult
    return c, info, delay


def best_true_action(case, fn_mult=1.0):
    s, amt = case["true_state"], case["amount"]
    t = M.cost_table(amt, scaled=True)
    return min(M.ACTIONS, key=lambda a: t[a][s] * (fn_mult if a == "Ignore" and s != "Normal" and s != "Planned" else 1.0))


def score(cases, decisions, fn_mult=1.0, price_mult=1.0):
    n = len(cases)
    tp = fp = fn = 0
    acc = review = q = 0
    dec_cost = info_cost = delay_cost = 0.0
    missed_c = wrong_limit = 0
    logloss, pairs = 0.0, []
    for c, d in zip(cases, decisions):
        s, a = c["true_state"], d["action"]
        dc, ic, dl = true_cost(c, a, d["checks"], fn_mult, price_mult)
        dec_cost += dc
        info_cost += ic
        delay_cost += dl
        acc += a == best_true_action(c, fn_mult)
        review += a == "Report"
        q += len(d["checks"])
        bad, alert = s in PROBLEM, a in ("Report", "Limit")
        tp += bad and alert
        fp += (not bad) and alert
        fn += bad and not alert
        missed_c += s == "Compromise" and a == "Ignore"
        wrong_limit += s in ("Normal", "Planned", "Other") and a == "Limit"
        p_true = max(d["belief"].get(s, 0.0), 1e-6)
        logloss += -log2(p_true)
        pairs.append((sum(d["belief"].get(x, 0.0) for x in PROBLEM), bad))
    return {
        "cases": n,
        "accuracy": acc / n,
        "precision": tp / (tp + fp) if tp + fp else float("nan"),
        "recall": tp / (tp + fn) if tp + fn else float("nan"),
        "false_positives": fp, "false_negatives": fn,
        "missed_compromises": missed_c, "wrong_limits": wrong_limit,
        "decision_cost": dec_cost, "info_cost": info_cost, "delay_cost": delay_cost,
        "total_cost": dec_cost + info_cost + delay_cost,
        "questions_per_case": q / n, "human_review_rate": review / n,
        "cross_entropy_bits": logloss / n,
        "ece": ece(pairs),
    }


def ece(pairs, bins=(0, .1, .3, .5, .7, .9, 1.01)):
    """Expected calibration error for P(problem)."""
    tot, n = 0.0, len(pairs)
    for lo, hi in zip(bins[:-1], bins[1:]):
        b = [(p, y) for p, y in pairs if lo <= p < hi]
        if b:
            tot += len(b) / n * abs(sum(p for p, _ in b) / len(b) - sum(y for _, y in b) / len(b))
    return tot


def reliability(pairs, bins=(0, .1, .3, .5, .7, .9, 1.01)):
    rows = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        b = [(p, y) for p, y in pairs if lo <= p < hi]
        if b:
            rows.append((lo, min(hi, 1.0), len(b), sum(p for p, _ in b) / len(b), sum(y for _, y in b) / len(b)))
    return rows
