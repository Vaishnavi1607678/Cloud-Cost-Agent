# Failure Analysis

Failures F1–F6 come from **v1 Policy C on the development set** (`data/cases.csv`, seed 42).
They were used to design v2. Failures F7–F8 come from **v2 on the holdout set** (`data/cases_holdout.csv`, seed 2026), which was created after v2 was designed.

Cost = decision cost from the cost table in `src/agent.py` (+$25 if the agent investigated).

| ID | Failure name | Case | True state | Agent action | Cost | Fixed in v2? |
|---|---|---|---|---|---|---|
| F1 | Quiet compromise | dev C28 | Compromise | Ignore | **$5,000** | Yes, mostly |
| F2 | Usage spike hidden by price noise | dev C06 | Waste | Ignore | $400 | Yes |
| F3 | Compromise through a trusted identity | dev C27 | Compromise | Report (not Limit) | $625 | No, open question |
| F4 | Invisible spike on a cheap day | dev C12 | Waste | Ignore | $400 | No |
| F5 | Insurance reporting of planned jobs | dev C11, C13 | Planned | Report | $75 each | No, design trade-off |
| F6 | Price-noise false alarm | dev C08, C15 | Normal | Report | $75 each | No |
| F7 | Untracked planned job looks like a hack | holdout C13 | Planned | **Limit** | **$1,525** | New in v2 |
| F8 | Unread change ticket | holdout C29, C35 | Planned | Report | $50 each | No |

---

## F1 — Quiet compromise (dev C28) — highest-cost failure

- **What happened:** A compromise case on Lambda, but today's cost was *lower* than the 7-day median (cost ratio 0.46, usage ratio 1.26). The region was not new, so the agent saw nothing unusual. P(Compromise) = 0.1%, and it chose **Ignore** without investigating.
- **Evidence it never looked at:** the owner tag was missing, the launcher was unknown, and there was no change ticket. All three clues pointed to compromise.
- **Why:** In v1, every clue had to be paid for through Investigate. Investigation only looks "worth it" when the cost signal is already unusual, so a compromise with no visible spike is never investigated.
- **Fix in v2 (Change 2):** Reading the owner tag is a free API call, so v2 always reads it. In the ablation, this alone cut missed compromises from 0.57 to 0.10 per 40 cases.
- **Partly a data artifact:** the mock data is very noisy, and the injected spike landed on a low-cost day.

## F2 — Usage spike hidden by price noise (dev C06)

- **What happened:** A waste case where cost rose only 1.32× but **usage rose 8.74×**. v1 used only cost, saw "low", and ignored it.
- **Why:** In the mock data, the price per unit changes randomly from day to day, so cost alone hides usage changes.
- **Fix in v2 (Change 1):** spike = max(cost ratio, usage ratio). In the ablation, this alone cut average decision cost from $6,656 to $4,732 per 40 cases.

## F3 — Compromise through a trusted identity (dev C27)

- **What happened:** A 26× cost spike. The agent investigated: owner tag missing, **launcher known**, no ticket. The known launcher pulled P(Compromise) down to 12%, so it chose Report instead of Limit.
- **Why it matters:** With stolen keys, CloudTrail shows the *real user's* identity. "Known launcher" may be weak evidence against compromise. My likelihood P(known launcher | Compromise) = 0.20 may be too low.
- **Not changed:** Changing this without real evidence would just be tuning to my own simulation. **This is a question for Reddit (r/aws, r/cybersecurity).**

## F4 — Invisible spike on a cheap day (dev C12)

- **What happened:** A waste case with cost ratio 0.05 and usage ratio 0.20. The injected 1.5–3.5× spike landed on a day whose base value was already near zero.
- **Why:** No cost-based signal can detect this. It is mainly a weakness of the mock data and my case generator, and is recorded as a limitation.

## F5 — Insurance reporting of planned jobs (dev C11, C13)

- **What happened:** After investigation, P(Planned) = 80% and the change ticket was present, but the agent still chose **Report**.
- **Why:** P(Compromise) was still 2.2%. Expected cost of Ignore = 0.045 × $400 + 0.022 × $5,000 ≈ $128, which is higher than Report ≈ $62. Because a missed compromise costs $5,000, any compromise risk above roughly 1% makes "tell a human" the cheaper choice.
- **Meaning:** The cost table has no penalty for **alert fatigue**. If engineers start ignoring reports, the true cost of Report is much higher than $50. This is a key question for practitioners.

## F6 — Price-noise false alarm (dev C08, C15)

- **What happened:** Normal EC2 days with cost 4.3× the median. In C15, usage actually *fell* (0.75×). Only the price per unit jumped.
- **Why:** Random price noise in the mock data. In real AWS data, a unit-price jump alone could mean a pricing change, a lost discount, or a different instance type. These could be extra hidden states.

## F7 — Untracked planned job looks like a hack (holdout C13) — highest-cost v2 failure

- **What happened:** A planned CloudFront job, but nobody tagged the resource, and the launcher and ticket were both missing. After investigation, P(Compromise) = 72%, above the 50% guard. The agent chose **Limit** and broke a real workload: **$1,525**.
- **Why:** Free owner-tag evidence (Change 2) strongly links "no tag" with compromise. Teams that do not tag their resources look like attackers.
- **Ablation:** wrong Limits rose from 0.03 (v1) to 0.20–0.23 per 40 cases, caused by the free-tag change.
- **Next change (v3 idea):** require human approval for every Limit, or raise the guard threshold. The 50% guard alone did not help in the ablation; it only increased cost ($6,656 → $7,073).

## F8 — Unread change ticket (holdout C29, C35)

- **What happened:** Planned jobs that had a change ticket. The agent did not pay $25 to investigate, so it never saw the ticket, and it reported them.
- **Why:** The free owner tag already made the agent "fairly sure" it was not a compromise, so investigating seemed not worth $25. Report was cheap anyway.
- **Idea:** reading change tickets could also be automatic and free (for example, from a deploy calendar).

---

## Which error has the highest cost, and why

**Ignoring a compromise ($5,000 in my cost table) is the highest-cost error.**

1. **It grows over time.** An attacker's mining instances keep running every hour until someone notices. The other errors are one-time costs.
2. **It is more than money.** The same leaked keys can read data or create new users, so it becomes a security incident.
3. **It is hard to correct.** A wrong Limit can be undone by restarting the workload. Time lost to an attacker cannot be undone.
4. **The cost falls on the company, not the team that leaked the key.**

The second-highest is **limiting a planned production job ($1,500)**: it causes our own outage, but it is visible and quickly reversible.

**v2's trade-off:** v2 almost removes the first error (missed compromises 0.57 → 0.10 per 40 cases), but it increases the second (wrong Limits 0.03 → 0.20). With my cost table, this trade is worth it, but it depends on whether the $5,000 vs $1,500 values are realistic. That needs human input.
