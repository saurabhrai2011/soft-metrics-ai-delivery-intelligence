# User Personas

This document defines the primary users of the Software Metrics AI Delivery Intelligence platform. Each persona is grounded in real engineering org workflows and is referenced by ID throughout the rest of the specification.

---

## Persona 1 — Maya Chen, Engineering Manager (`EM-01`)

| Attribute | Detail |
|---|---|
| **Role** | Engineering Manager owning 2 squads (14 engineers) at a 500-person SaaS company |
| **Tenure** | 3 years as EM, 8 years as IC before that |
| **Tools used daily** | Jira, GitHub, Slack, Lattice, Google Sheets |
| **Reports to** | Director of Engineering |
| **Key responsibilities** | Sprint health, 1:1s, performance reviews, hiring, stakeholder updates |

### Goals
- Spot delivery risk before her director does
- Identify which engineer is overloaded vs. underutilized
- Have data-backed conversations in 1:1s and reviews
- Reduce time spent assembling weekly status reports (currently ~4 hrs/week)

### Pain points
- Jira reports require manual filtering; she ends up exporting to Sheets
- Can't easily correlate code review delays with sprint slippage
- Burnout signals (working hours, after-hours commits) are invisible until someone resigns
- Weekly reports are stale by the time she sends them

### What success looks like
> "I open the product on Monday morning, and within 2 minutes I know which sprint commitments are at risk this week, who's blocked, and what to address in my 1:1s — without opening Jira."

---

## Persona 2 — Raj Patel, Delivery Lead / TPM (`TPM-01`)

| Attribute | Detail |
|---|---|
| **Role** | Senior TPM coordinating 6 teams on a customer-facing platform program |
| **Tenure** | 5 years TPM experience, PMP certified |
| **Tools used daily** | Jira Advanced Roadmaps, Confluence, Smartsheet, Slack, Looker |
| **Reports to** | Director of Program Management |
| **Key responsibilities** | Cross-team dependencies, predictability, risk communication, executive updates |

### Goals
- Predict whether quarterly commitments will land on time — *now*, not in the QBR
- Identify cross-team dependency risks before they block a team
- Quantify flow efficiency (work-time vs. wait-time) across the program
- Reduce "surprise slippage" reported to leadership

### Pain points
- Roadmap data lives in Jira; risk narratives live in Confluence; status lives in Slack — nothing connects
- Dependency risks surface 2–3 weeks too late
- Spends ~6 hours/week building exec status decks
- Has no quantitative way to show that "Team Beta is the bottleneck"

### What success looks like
> "I get an alert on Tuesday saying 'Epic X is now 70% likely to slip by 2+ sprints due to Team Beta's review backlog.' I escalate Tuesday — not in the QBR three weeks later."

---

## Persona 3 — Priya Sharma, VP of Engineering (`VPE-01`)

| Attribute | Detail |
|---|---|
| **Role** | VP Engineering, owning 80 engineers across 8 teams |
| **Tenure** | 12 years engineering leadership |
| **Tools used daily** | Slack, Google Slides, Jellyfish/LinearB (existing eng intelligence), email |
| **Reports to** | CTO |
| **Key responsibilities** | Org-level health, hiring plans, R&D budget, board reporting |

### Goals
- Portfolio-level signal: which teams are healthy, which are at risk, which are improving
- Trends, not snapshots — is throughput improving quarter-over-quarter?
- Concise, narrative-driven insights she can take to the CEO and board
- Confidence that what she reports upward is accurate

### Pain points
- Existing eng intelligence tools give metrics, not narratives
- Has to manually construct stories from charts for board updates
- Can't easily tell whether a metric change is meaningful or noise
- Reactive — usually learns about delivery risk from skip-levels, not data

### What success looks like
> "Before my board prep, I ask: 'Summarize engineering delivery health for Q2 with notable risks and wins.' I get a 3-paragraph narrative I can paste into my deck — with evidence links."

---

## Persona 4 — Alex Rivera, Scrum Master / Tech Lead (`TL-01`)

| Attribute | Detail |
|---|---|
| **Role** | Tech Lead doubling as Scrum Master for an 8-person platform team |
| **Tenure** | 6 years engineering, first time leading |
| **Tools used daily** | Jira, GitHub, Datadog, IntelliJ, Slack |
| **Reports to** | Engineering Manager |
| **Key responsibilities** | Sprint ceremonies, team flow, technical decisions, retro facilitation |

### Goals
- Identify what's blocking the team's flow this sprint
- Bring data to retros (not opinions)
- Improve PR cycle time and WIP discipline
- Catch quality regressions early (escaped defects, flaky tests)

### Pain points
- Retros are opinion-driven; no quantitative grounding
- PR review delays are common but no one tracks them systematically
- "Done" definitions vary by engineer; rework is invisible
- Production incidents arrive without context for the team

### What success looks like
> "Before retro, I ask: 'What were the top 3 flow bottlenecks this sprint?' I get specifics — 'PR #2341 sat 4 days awaiting review from @mike' — and the retro becomes constructive instead of vague."

---

## Persona priority for MVP

| Priority | Persona | Rationale |
|---|---|---|
| **P0** | EM-01 (Maya) | Highest frequency of use; primary buyer in mid-market |
| **P0** | TPM-01 (Raj) | Strongest pain point around cross-team prediction |
| **P1** | TL-01 (Alex) | Daily user, but lighter feature surface needed |
| **P2** | VPE-01 (Priya) | Strategic importance, but lower query volume |

---

## Anti-personas (users we are not designing for)

- **Individual contributors looking for personal productivity metrics** — we will not build a tool that measures individual engineers against each other.
- **HR / People Ops looking for performance-management data** — engineering data is not a performance review input.
- **Finance looking for engineering cost attribution** — out of scope for this product.