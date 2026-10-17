# Cloud Cost Agent

> **Week 1:** [`week1/deliverables/student-project/`](week1/deliverables/student-project/): agent design, 40-case test, failure analysis, AI reviews, preprint.
> **Week 2:** [`week2/`](week2/): which check to run next and when to act: entropy, information gain, value of information, 500-case × 20-seed experiment, shift alarm, feedback bias. See the [Week 2 README](week2/README.md).

**An agent that decides what to do about an unusual AWS cost when it cannot see the real cause.**

> The agent observes a daily AWS cost line item (service, region, usage, cost) and that service's recent history. It must choose to **ignore, investigate, limit, or report** the cost because the **cause of the cost change** is not known.

This is my Week 1 AI-Native project. The agent keeps a probability for each possible cause, weighs the dollar cost of each possible mistake, and can pay a small price to investigate before it acts.

---

## Why this problem

When an AWS bill jumps, the bill alone does not tell you *why*:

| Hidden cause | Example | What happens if we get it wrong |
|---|---|---|
| **Normal** | Ordinary daily variation | Alerting wastes an engineer's time |
| **Planned** | Batch job, load test, launch traffic | Shutting it down causes our own outage |
| **Waste** | Forgotten instance, Lambda retry loop | Money leaks slowly |
| **Compromise** | Leaked keys running crypto-mining | Bill grows every hour, security incident |

A simple "cost is too high → alert" rule treats all four the same. This project tests whether an agent that reasons about **probability and cost** makes cheaper decisions.

---

## How the agent works

```
 Cost row + 7-day history
          │
          ▼
 Belief over 4 hidden states   ← prior × likelihood (Bayes' rule)
          │
          ▼
 Is investigating worth $25?   ← compares expected cost with / without more evidence
     │ yes                │ no
     ▼                    │
 Check owner tag,         │
 CloudTrail launcher,     │
 change ticket            │
 → update belief          │
     │                    │
     ▼                    ▼
 Choose action with the lowest expected dollar cost
 (Ignore · Report to human · Limit resource)
```

**Human reasoning function:** *change a belief after new evidence.* The agent updates its belief with Bayes' rule after it investigates.

---

## Results (40 simulated cases)

| | Baseline (threshold) | A: most likely state | B: lowest expected cost | **C: B + investigate** |
|---|---|---|---|---|
| Compromises missed (of 7) | 3 | 5 | 1 | **1** |
| Problems caught (recall) | 50% | 13% | 81% | **81%** |
| False alarms | 6 | 2 | 14 | **8** |
| Good workloads wrongly limited | 0 | 2 | 2 | **0** |
| Total decision cost | $19,860 | $31,800 | $12,280 | **$8,605** |

**Main findings**
- Policy C reduced total decision cost by about **57%** compared with a standard threshold alert.
- Investigating before acting cut false alarms from 14 to 8 compared with B.
- Choosing the *most likely* cause (Policy A) was the worst policy. Compromises are rare, so they are almost never the most likely cause, and A missed 5 of 7. **The cost of a mistake matters as much as its probability.**

Full metrics are in [`results/metrics.md`](week1/deliverables/student-project/results/metrics.md).

### Version 2 (built from the failure analysis)

I examined the wrong decisions and named 8 failure conditions ([`failure-analysis.md`](week1/deliverables/student-project/results/failure-analysis.md)). The worst was a **"quiet compromise"**: a hack with no cost spike, which v1 ignored even though the resource had no owner tag. v2 adds four changes:

| Change | Fixes |
|---|---|
| Spike uses usage as well as cost | Usage spikes hidden by price noise |
| Owner tag is checked automatically (free API call) | Quiet compromises |
| Learns from feedback after each decision | Agent never improved |
| Limit only if P(Compromise) ≥ 50% | Human control on the most harmful action |

To test v2 fairly, I used a **new holdout set** it had never seen, then repeated the test on **30 random case sets**:

| Mean per 40 cases (30 sets) | Baseline | v1 (C) | **v2** |
|---|---|---|---|
| Total decision cost | $17,781 | $6,656 | **$4,038** |
| Recall | 49% | 76% | **90%** |
| Missed compromises | 2.47 | 0.57 | **0.10** |
| False alarms | 5.8 | 8.7 | 14.2 |
| Good workloads wrongly limited | 0.00 | 0.03 | 0.20 |

v2 was cheaper than v1 in **25 of 30** sets (sign test p = 0.0003). A fairer threshold baseline that also watches usage costs $12,214, still about 3× more than v2. v2 also stays the cheapest when the cost and prior guesses are changed ([sensitivity](week1/deliverables/student-project/results/sensitivity.md)). **The trade-off:** v2 almost never misses a hack, but it raises more false alarms and sometimes shuts down a planned job that nobody tagged ("untracked planned job looks like a hack"). The ablation study shows the free owner-tag check causes both the biggest gain and this new failure. Learning from feedback had little effect with only 40 cases.

A full worked Bayes example on a real, unlabeled billing row is in [`probability-decision-record.md`](week1/deliverables/student-project/decisions/probability-decision-record.md).

---

## Run it yourself

Requirements: Python 3.9+ (`matplotlib` is optional, only needed for the figures).

```bash
git clone https://github.com/Vaishnavi1607678/Cloud-Cost-Agent.git
cd Cloud-Cost-Agent/week1/deliverables/student-project
pip install matplotlib                 # optional
python3 src/make_cases.py              # builds 40 test cases (fixed seed = 42)
python3 experiments/run_experiment.py  # runs all policies and writes results/
```

Full steps for v2, the holdout set, and the robustness and ablation runs are in the [project README](week1/deliverables/student-project/README.md).

The agent makes all its decisions **before** the true labels are loaded.

---

## Repository structure

```
week1/deliverables/student-project/
├── README.md                    # how to repeat the test
├── research-file.md             # terms, communities, sources, questions
├── discussion-record.md         # Reddit and X discussions → design changes
├── review-record.md             # AI reviews, accepted/rejected with reasons
├── data/                        # mock AWS billing data + generated cases
├── src/
│   ├── agent.py                 # v1: beliefs, Bayes update, costs, policies
│   ├── agent_v2.py              # v2: changes from the failure analysis
│   └── make_cases.py            # builds labeled test cases
├── experiments/                 # v1, v2, robustness and ablation runs
├── results/                     # metrics, predictions, figures, failure analysis
├── decisions/                   # probability decision record
├── paper/                       # IJCAI-style LaTeX preprint
└── social/                      # LinkedIn post and X thread
```

---

## Limitations (please read)

- **Simulated data.** The billing data is mock data, and the anomaly cases were injected using my own assumptions, not real incidents.
- **Estimated costs.** The dollar cost of each mistake (for example, $5,000 for a missed compromise) is my estimate and still needs checking with practitioners.
- **Small test.** 40 cases is small; the numbers are indicative, not proof.
- **Daily data.** Real compromises may need hourly data to catch in time.
- **Human control.** The *Limit* action could stop production workloads. In real use it should require human approval.

---

## Project status

- [x] Problem selected and research file created
- [x] Agent built and tested against a baseline
- [x] Failure analysis (8 named failures) and probability decision record
- [x] Agent v2 tested on a holdout set, 30 random sets, and an ablation study
- [ ] Reddit and X discussions
- [x] Three AI reviews with accepted and rejected comments ([review-record.md](week1/deliverables/student-project/review-record.md))
- [x] Preprint draft in LaTeX ([PDF](week1/deliverables/student-project/paper/preprint-draft.pdf))
- [ ] Add human discussion results to the paper and build with the official IJCAI kit
- [ ] LinkedIn post and X thread

---

## Week 2 in one paragraph

The agent now chooses which evidence to buy. The most accurate policy (picking the most likely cause, 87%) costs **4.4×** more than the final cost-aware agent. The most informative check (a $2,000 security investigation, 0.63 bits) has a value of **−$2,414**, while a $1 CloudTrail lookup is worth **+$55**: in only 2 of 600 situations was the most informative check the best buy. When the agent's model of the evidence is wrong, its advantage mostly disappears (12 of 20 seeds). Details: [Week 2 README](week2/README.md).

## Feedback wanted

I'd especially like comments on:
1. Are there hidden causes I missed?
2. Are my error costs realistic?
3. When would you trust an agent to limit a resource automatically?

Open an issue or reach out on X.

---

## AI use

I used AI assistants (Claude) to prepare research questions, write and debug code, and draft documentation. I checked, ran, and am responsible for all content in this repository. All reported results come from running the code in this repository.
