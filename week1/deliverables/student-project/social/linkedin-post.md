# LinkedIn post (draft): publish only ONE this week, with the final preprint PDF attached

Before posting:
- [ ] Replace the [DISCUSSION] line with a real design change from Reddit/X
- [ ] Attach the final `paper/preprint.pdf` (official IJCAI style)
- [ ] Read it aloud and change any wording that doesn't sound like you

---

When an AWS bill jumps, you have to decide what to do before you know why.

That's the problem I studied for my Week 1 AI-Native project:

An agent sees one daily AWS cost line and its 7-day history. It must ignore, investigate, limit, or report the cost, without knowing if the cause is normal variation, a planned job, waste, or leaked keys.

Why this design: a threshold alert only says "this is unusual". The right action depends on the cause, and each wrong action has a different price. Ignoring a compromise is far worse than an extra alert. Shutting down a planned job causes your own outage.

Why a probability model: the agent keeps a probability for each of the 4 causes, updates it with Bayes' rule as clues arrive (owner tag, CloudTrail launcher, change ticket), and picks the action with the lowest expected cost. It can also decide that a $25 investigation is worth it before acting.

What I found (simulation, 30 random sets of 40 cases):
• The cost-aware agent cut decision cost from $17,781 to $4,038 vs a threshold alert
• Missed compromises dropped from 2.5 to 0.1
• "Pick the most likely cause" was the worst policy of all. Compromises are rare, so they're never the most likely cause, even when they're the most expensive to miss.

A failure I caused myself: making the owner-tag check free removed most missed compromises, but the agent then shut down planned jobs that nobody had tagged. Untagged legitimate work looks like an attack.

What changed after public discussion: [DISCUSSION: e.g. "an engineer on r/aws pointed out that ___, so I changed ___"]

Largest limitation: the test cases were generated with assumptions close to the agent's own, using mock billing data. These results show the decision rule is consistent, not that it works on real incidents.

My question for FinOps / SRE folks: what does one unnecessary cost alert really cost your team? My results change a lot depending on that number.

Preprint attached. Code: https://github.com/Vaishnavi1607678/Cloud-Cost-Agent

#FinOps #AWS #DevOps #SRE #AIAgents
