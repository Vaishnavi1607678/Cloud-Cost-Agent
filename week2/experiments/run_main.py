"""
run_main.py - Main Week 2 experiment (brief Section 18).
500 simulated cases, seed 42, every policy on the identical cases.
Outputs: results/main_metrics.md/.json, results/predictions_main_<policy>.csv
"""
from common import N, POLICY_SET, RESULTS, SEED, S, dump, run, save_predictions, table

KEYS = ["accuracy", "precision", "recall", "false_positives", "false_negatives",
        "missed_compromises", "wrong_limits", "decision_cost", "info_cost", "delay_cost",
        "total_cost", "questions_per_case", "human_review_rate", "cross_entropy_bits", "ece"]
MONEY = ("decision_cost", "info_cost", "delay_cost", "total_cost")


def main():
    cases = S.make_cases(N, SEED)
    counts = {s: sum(c["true_state"] == s for c in cases) for s in ["Normal", "Planned", "Waste", "Compromise", "Other"]}
    res = {}
    for name, (fn, kw) in POLICY_SET.items():
        dec, m = run(cases, fn, kw)
        res[name] = m
        save_predictions(RESULTS / f"predictions_main_{name.split()[0]}.csv", cases, dec)
    md = [f"# Main experiment: {N} simulated cases, seed {SEED}, matched simulator", "",
          f"True states in this sample: {counts}", "", table(res, KEYS, MONEY)]
    (RESULTS / "main_metrics.md").write_text("\n".join(md) + "\n")
    dump("main_metrics.json", {"seed": SEED, "n": N, "state_counts": counts, "results": res})
    print("\n".join(md))


if __name__ == "__main__":
    main()
