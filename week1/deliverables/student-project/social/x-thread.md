# X thread (draft): attach the same preprint PDF to post 1

Before posting:
- [ ] Attach the final `paper/preprint.pdf` (or images of its pages) to post 1
- [ ] Fill the [DISCUSSION] post with a real change from Reddit/X, or delete that post
- [ ] Check every post is under 280 characters

---

**1/**
AWS bill jumps. Is it normal, a planned job, waste, or leaked keys?

You have to act before you know.

I built a small agent that decides: ignore, investigate, limit, or report. Preprint 👇

**2/**
Problem: the agent sees 1 daily cost line + 7 days of history.

It keeps a probability for each of the 4 causes, updates it with Bayes' rule, and picks the action with the lowest expected $ cost. It can pay $25 to investigate first.

**3/**
Test: mock AWS billing data with injected problems. 40 cases per set, 30 random sets, labels hidden until after each decision.

Compared: threshold alert vs most-likely-cause vs cost-aware agent.

**4/**
Result:
Threshold alert: $17,781 in decision cost, 2.5 missed compromises
Cost-aware agent: $4,038, 0.1 missed

Surprise: "pick the most likely cause" was the worst. Rare ≠ cheap to miss.

**5/**
Trade-off: the agent raises more false alarms (14 vs 6 per 40 cases), and sometimes shuts down planned jobs nobody tagged.

Untagged legit work looks like an attack.

**6/**
[DISCUSSION: one design change from a Reddit/X discussion]

**7/**
Biggest limitation: the test cases share the agent's own assumptions. It's a simulation, not real incidents.

Open question: what does one unnecessary cost alert really cost your team? The answer changes everything.

Code: https://github.com/Vaishnavi1607678/Cloud-Cost-Agent
