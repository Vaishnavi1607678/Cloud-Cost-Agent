# Research File — Cloud Cost Agent

## 1. Problem statement

> The agent observes a daily AWS cost line item (service, region, usage, cost) and that service's recent history. It must choose to **ignore, investigate, limit, or report** the cost because the **cause of the cost change** is not known.

## 2. Project objective

Build a small agent that decides what to do about an unusual cloud cost when it cannot see the real cause. Test whether a cost-aware probability policy makes cheaper decisions than a simple threshold alert.

## 3. Agent summary

| Part | Value |
|---|---|
| Input | Date, Service, Region, UsageType, UsageAmount, Cost, plus the last 7 days for that service |
| Hidden states | Normal, Planned spike, Waste/misconfiguration, Compromise |
| Belief | Probability of each hidden state (sum = 100%) |
| Actions | Ignore, Investigate, Limit, Report |
| Human reasoning function | Change a belief after new evidence (Bayes' rule) |
| Data | `data/aws_billing_data_mock.csv`: 150 rows, 5 services, 1–30 Jul 2025, mock data with no labels |

## 4. Technical terms

- **FinOps**: the practice of managing cloud spending as a team activity
- **Cost anomaly detection**: finding cost values that differ from the expected pattern
- **Baseline / expected spend**: what cost "should" be (for example, a 7-day average)
- **z-score**: how many standard deviations a value is from the average
- **Unit cost**: Cost ÷ UsageAmount. A change here means something different from a change in usage.
- **Cost allocation tags**: labels on resources showing the owner/team. A missing tag is a useful clue.
- **CloudTrail**: the AWS log of who did what. Used to check who launched a resource.
- **AWS Budgets / budget actions**: automatic limits when spend passes a threshold
- **Cryptojacking**: attackers using stolen cloud keys to mine cryptocurrency
- **Prior / likelihood / posterior**: belief before evidence / chance of evidence in each state / belief after evidence
- **False positive / false negative**: alerting on a normal cost / missing a real problem
- **Expected cost of an action**: Σ P(state) × cost(action, state)
- **Human-in-the-loop / escalation**: sending a decision to a person

## 5. Search queries

- `AWS cost anomaly detection false positives`
- `unexpected AWS bill leaked access keys crypto mining`
- `Lambda recursive loop huge bill`
- `forgotten EC2 instance cost`
- `FinOps anomaly alert fatigue`
- `AWS budget action stop instances production outage`
- `site:reddit.com/r/aws surprise bill`
- `cloud cost anomaly detection paper`
- `Bayesian decision theory alerting cost-sensitive`

## 6. Reddit communities (verify each before posting)

| Community | Why relevant | Verified active? | Rules allow questions? |
|---|---|---|---|
| r/aws | Many "surprise bill" posts; AWS users | ☐ | ☐ |
| r/FinOps | Cloud cost management practitioners | ☐ | ☐ |
| r/devops | Engineers who handle alerts and budgets | ☐ | ☐ |
| r/sre | Alert fatigue, incident decisions | ☐ | ☐ |
| r/sysadmin | People who get the bill and the blame | ☐ | ☐ |
| r/cloudcomputing | General cloud audience | ☐ | ☐ |
| r/AZURE | Same problem on another cloud (comparable cases) | ☐ | ☐ |
| r/googlecloud | Same problem on another cloud | ☐ | ☐ |
| r/MachineLearning or r/learnmachinelearning | Feedback on the probability model | ☐ | ☐ |
| r/cybersecurity | Compromise / cryptojacking state | ☐ | ☐ |

Check: last post within the last few days, member count, and the sidebar rules. Remove any community that fails. Keep **5–10**.

### Posting plan: a different angle for each community (Section 5: do not copy the same text)

Write each post in your own words. Two contributions per community, for example one new post and one comment on an existing thread.

| Community | Angle that fits its purpose | Question to ask |
|---|---|---|
| r/aws | Real AWS evidence | With leaked keys, does CloudTrail show the real user's identity? Which clue made you suspect compromise first? |
| r/FinOps | Cost of errors | Is ~$5,000 a realistic cost for a compromise found a day late? What does an unneeded alert really cost your team? |
| r/devops | Automated actions | Would you let a tool auto-stop an **untagged** resource during a cost spike? What went wrong when you tried? |
| r/sre | Alert fatigue | How many cost alerts per week before people ignore them? My agent sends ~57% of cases to a human; is that unusable? |
| r/sysadmin | Who pays | When a surprise bill happens, who ends up paying the cost, and what did you check first? |
| r/cybersecurity | Compromise state | Which signals separate cryptojacking from a forgotten resource on a bill? |
| r/cloudcomputing | Hidden states | Did I miss a cause of cost spikes (price change, expired Savings Plan, billing delay)? |
| r/AZURE / r/googlecloud | Comparable cases | Are cost spikes on your cloud caused by the same four things? |
| r/learnmachinelearning | Probability model | Is naive Bayes OK when "no owner tag" and "unknown launcher" are correlated? |

## 7. X accounts (verify each before following)

Look for these kinds of people: cloud cost/FinOps practitioners, AWS engineers, SREs who write about alerting, cloud security researchers (cryptojacking), and anomaly-detection researchers.

**Section 6 says to find these with ChatGPT or Gemini.** Paste this prompt into one of them:

```text
My problem: an agent observes a daily AWS cost line item and its 7-day history and must
choose to ignore, investigate, limit, or report the cost because the cause (normal,
planned job, waste, or compromised keys) is not known.
Objective: test whether a cost-aware Bayesian agent makes cheaper decisions than threshold alerts.
Find 25 X accounts I should follow: FinOps practitioners, AWS/SRE engineers, cloud security
researchers (cryptojacking, leaked keys), anomaly-detection researchers, and critics of
automated remediation. Not only popular AI accounts. For each: handle, who they are,
why relevant, and an example topic they post about. Mark anything you are unsure of.
```

Then open every account and keep it only if it posted about cloud cost, alerting, or cloud security recently. Target: **15–25 accounts**, with a mix of researchers, engineers, users, and critics.

| # | Account | Type (researcher / engineer / user / critic) | Why relevant | Recent relevant post? | Keep? |
|---|---|---|---|---|---|
| 1 | @QuinnyPig (Corey Quinn) | Engineer / commentator | Writes about AWS bills | ☐ | ☐ |
| 2 | | | | ☐ | ☐ |
| … | | | | | |
| 25 | | | | ☐ | ☐ |

Do not keep an account only because it is popular.

## 8. Papers, articles, repositories, datasets (read before citing)

| # | Source | Why useful | Read? |
|---|---|---|---|
| 1 | AWS documentation: *AWS Cost Anomaly Detection* | The real-world baseline product | ☐ |
| 2 | FinOps Foundation: *FinOps Framework*, "Anomaly Management" capability | Practitioner definition of the problem | ☐ |
| 3 | Chandola, Banerjee, Kumar (2009). *Anomaly Detection: A Survey*. ACM Computing Surveys | Standard background reference | ☐ |
| 4 | Guha et al. (2016). *Robust Random Cut Forest Based Anomaly Detection on Streams*. ICML | Streaming anomaly method | ☐ |
| 5 | Hochenbaum, Vallis, Kejariwal (2017). *Automatic Anomaly Detection in the Cloud via Statistical Learning*. arXiv | Cloud-metric anomaly detection (Twitter) | ☐ |
| 6 | Elkan (2001). *The Foundations of Cost-Sensitive Learning*. IJCAI | Why error costs change the decision | ☐ |
| 7 | Howard (1966). *Information Value Theory*. IEEE Trans. Systems Science and Cybernetics | Why the agent pays to investigate (value of information) | ☐ |

Confirm every title, author, and year before adding it to `references.bib`.

## 9. Questions I want to answer

**Hidden states**
1. Did I miss a hidden state? (Example: AWS pricing change, or billing data delay)
2. Can a human tell Waste from Compromise by looking at the bill alone?

**Evidence**
3. Which single piece of evidence most changes your belief? (Owner tag, CloudTrail user, region, time of day?)
4. Is a jump in unit cost a different signal from a jump in usage?

**Actions**
5. When is it acceptable for an agent to automatically limit (stop or scale down) a resource?
6. When must the agent ask a human?

**Errors and costs**
7. Which costs more in practice: a missed compromise or a wrong shutdown of production?
8. How many false alerts per week before a team ignores the alerts?

**Data**
9. Is 30 days of history enough? Is a 7-day baseline comparable across weekends and month-end?

## 10. Claims that need a source or a test

- "Threshold alerts cause alert fatigue." → needs a source or human discussion
- "Compromise is the highest-cost error." → needs discussion and a cost estimate
- "The cost-aware policy has lower decision cost than the baseline." → needs my test
- "Missing owner tags make compromise more likely." → assumption; ask practitioners

## 11. Unclear parts of my problem

- The data is mock: unit cost and region change randomly every day, and there are no labels. I will inject labeled simulated cases and state this as a limitation.
- Daily data is coarse; real compromises might need hourly data.
- The dollar costs of each error are my estimates and must be checked with humans.

## 12. AI prompts and AI errors

### Prompt used (the Section 4 course prompt)

```text
I am a beginner. I want to design an AI agent for this problem: The agent observes a daily
AWS cost line item (service, region, usage, cost) and that service's recent history. It must
choose to ignore, investigate, limit, or report the cost because the cause of the cost change
is not known.
The agent must make decisions when information is not complete.

Help me prepare my research.

1. Give me the technical terms for this problem.
2. Give me useful search queries.
3. Find 5 to 10 relevant Reddit communities.
4. Tell me why each community is relevant.
5. Find relevant researchers and engineers on X.
6. Give me questions about hidden states, evidence, actions, and errors.
7. Identify each claim that needs a source or a test.
8. Tell me which parts of my problem are not clear.

Do not present uncertain information as fact.
```

### Log of AI prompts and important AI errors

| Date | Tool | Prompt (short) | Important errors / things I had to check |
|---|---|---|---|
| 2026-10-17 | Claude | Section 4 research prompt (above) | Gave only 1 X account instead of 15–25; Reddit communities came from the AI's memory and are **not verified**; paper details had to be checked against the real papers (3 checked by web search) |
| 2026-10-17 | Claude | Build the agent and test cases | The case generator and the agent used similar assumptions, so the test is partly circular (found in review Q3) |
| 2026-10-17 | Claude | Failure analysis | An arithmetic slip: expected cost of Report was first written as $51; recomputed as $62 |
| 2026-10-17 | Claude | Decision record | The likelihood P(high spike \| Normal) = 0.05 was not checked against the data; the real historical rate is 0.122 (decision record, Part 4) |
| 2026-10-17 | Claude | LaTeX paper | Could not download the official IJCAI kit (blocked from its workspace); the paper uses a fallback layout until `ijcai26.sty` is added |
| 2026-10-17 | Claude | Reviews 1–3 | The same AI that wrote the code also reviewed it, so the reviews are not independent; an independent Gemini review is still required |

## 13. Answers to the Section 12 design questions

| Question | Answer for the cloud cost agent |
|---|---|
| **What can the agent observe?** | For free: service, region, usage type, usage amount, cost, the last 7 days of history, and (v2) the resource's owner tag. For $25 (Investigate): the CloudTrail launcher identity and whether a change ticket exists. |
| **What information is hidden?** | The cause of the cost change: Normal, Planned, Waste, or Compromise. Also hidden: whether the workload is production-critical, and whether a launcher identity was stolen. |
| **What will a human observe that the agent cannot?** | Team chat and meetings ("we're running a load test today"), business context (a launch or sale), knowledge of who left the team, whether a workload is critical, and the content of suspicious code or instances. |
| **What must the agent remember?** | The last 7 days of cost, usage, and regions per service; its past decisions and their revealed outcomes; and (v2) updated likelihood counts learned from that feedback. |
| **When must the agent ask a question?** | When the cheapest action is uncertain and investigating lowers expected cost (value of information > $25), and before any Limit where P(Compromise) < 50% (human guard). See F7: a Limit on an untracked planned job is why every Limit may need human approval. |
| **Which incorrect action can be corrected?** | A wrong Limit can be undone by restarting or raising the limit (an outage, but reversible). A wrong Report costs only engineer time. A wrong Ignore of a compromise **cannot** be undone: the money spent and any data accessed are lost. |
| **Who bears the cost of an incorrect action?** | Ignored compromise or waste: the company's cloud budget (and security team). Wrong Limit: the team whose workload breaks, and their users. Too many Reports: on-call engineers (alert fatigue). |
| **Which evidence changes the belief?** | Most: owner tag missing, a new region, and a high spike (≥3×) all raise P(Compromise). A change ticket strongly raises P(Planned). A known launcher lowers P(Compromise), but stolen keys may look like a known user (F3). |
| **Is the historical evidence comparable?** | Only partly. The data is 30 days of mock data with random price-per-unit noise and random region changes. Real billing has weekly patterns, month-end effects, and commitment discounts. No labeled real incidents were used. |
| **How does the agent learn after an action?** | (v2) After each decision, the true state is revealed. The agent adds one count to each observed evidence/state pair (Beta/Dirichlet pseudo-counts, starting strength 10). Result: learning reduced false alarms (15.7 → 14.2 per 40 cases) but did not reduce total cost on average ($3,838 → $4,038). 40 cases is too few to learn much. |
