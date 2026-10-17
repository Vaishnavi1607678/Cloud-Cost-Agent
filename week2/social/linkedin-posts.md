# Week 2 LinkedIn posts (5 drafts)

Brief §20.1: five posts connected to the project, at least one with something I actually discovered ("I assumed X. I tested it. X was wrong..."). Post them spread over the weeks, not all at once.
Before each: read it aloud, change anything that doesn't sound like me, and check every number against `results/`.

---

## Post 1 — The problem and why it is hard

When an AWS bill jumps, the bill doesn't tell you why.

It could be normal variation. A planned batch job. A forgotten instance. Leaked keys running crypto-mining. Or AWS changed a price.

Each cause needs a different response, and each wrong response has a different price:
• ignore a compromise → the bill grows until someone notices
• shut down a planned job → you cause your own outage
• alert on everything → people stop reading alerts

I'm building an agent that has to choose ignore / report / limit without seeing the cause. Week 2 question: which check should it run next, and when should it stop checking and act?

What's the first thing YOU check when a cost spike appears?

---

## Post 2 — A probabilistic insight: the threshold is 1%, not 80%

Most alert rules say something like "act if you're 80% sure it's a problem".

I derived my threshold from costs instead:
• false alarm: ~$50 of someone's time
• missing a compromise on a $60/day resource: ~$5,000 (hypothetical)

Break-even = 50 / (50 + 4,400) ≈ 1.1%.

So my agent should send a cost spike to a human at a 1% chance of compromise. On a $1,000/day resource it drops to 0.15%.

That only works because there are three actions, not two. "Report" is the cheap middle option that makes a 1% threshold usable.

Same maths as carrying an umbrella to a client demo at a 35% chance of rain.

---

## Post 3 — An information-theoretic insight: more bits ≠ more value

I priced the four checks my agent can buy at one uncertain case:

• CloudTrail lookup: 0.24 bits, $1 → worth +$55
• Ask the owning team: 0.52 bits, $40 + 2h → worth +$13
• Change-ticket search: 0.27 bits, $5 → worth −$6
• Full security investigation: 0.63 bits, $2,000 + 48h → worth −$2,414

The most informative check is the worst purchase. I then searched 600 situations: the most informative check was also the best buy in only 2 of them (0.3%).

Bits only matter when they can change what you do.

---

## Post 4 — A surprise (the "I assumed X" post)

I assumed more evidence always helps my agent.

I tested it in a simulated world where two clues are secretly linked: automation roles create untagged resources AND show up as unknown launchers in CloudTrail. My model treats those clues as independent.

Result: buying the CloudTrail check made the agent WORSE. It shut down 5.8 normal workloads per 500 cases (vs 1.2 when the clues really are independent), and cost more than a policy that never bought any check ($23,236 vs $19,433).

What I believe now: a true signal can hurt if your model counts it twice. I raised the bar for automatic shutdowns from 50% to 70% certainty: wrong shutdowns fell to 3.8, but the honest result is that in this world my agent only barely beats the simple policy.

Has anyone seen correlated "evidence" fool an alerting system like this?

---

## Post 5 — The preprint / most important finding

[Attach preprint PDF]

Week 2 of my AI-native engineering project: a probabilistic cloud-cost agent that decides what to check and when to act.

The most important thing I learned: **an agent that only hears about the problems it caught will slowly believe the world is safer than it is.**

When the agent ignores a cost spike, nobody complains, so in my simulation it counted every ignored case as "fine". Its estimate of waste got stuck at 10% (truth: 12%) and never corrected with more data. Auditing a random 5% of ignored cases, weighting each audit ×20, brought it back to 11.7%.

Everything is simulated and the costs are my assumptions. Which part would you trust least?

Code: https://github.com/Vaishnavi1607678/Cloud-Cost-Agent
