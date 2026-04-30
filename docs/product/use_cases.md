# Use Cases / User Journeys

This document captures the primary scenarios in which users interact with the platform. Each journey follows the format: **Goal → Trigger → Flow → Outcome → Persona reference**.

---

## UC-01 — Monday Morning Sprint Health Check

**Persona:** EM-01 (Maya)
**Frequency:** Weekly
**Priority:** P0 (MVP)

**Goal:** Understand sprint risk in under 5 minutes before standups.

**Trigger:** Maya opens the product on Monday at 8:30 AM.

**Flow:**
1. Landing view shows two squads with traffic-light health summaries (green/yellow/red) and a 1-sentence narrative each.
2. One squad shows yellow with: *"Sprint 47 commitment at risk — 3 stories blocked, 2 PRs aging >3 days."*
3. Maya clicks → drill-in shows the specific stories, owners, and root cause hypotheses.
4. She asks: *"Who should I talk to in 1:1s today?"*
5. The system suggests two engineers — one with stalled work, one with high after-hours activity.

**Outcome:** Maya walks into standup with specific, evidence-backed questions instead of generic "anything blocked?" prompts.

**Success indicator:** Maya uses the product on Monday mornings ≥ 3 weeks out of 4.

---

## UC-02 — Predicting Quarterly Slippage

**Persona:** TPM-01 (Raj)
**Frequency:** Weekly + ad-hoc
**Priority:** P0 (MVP)

**Goal:** Surface cross-team risk 4+ weeks before it materializes.

**Trigger:** Raj receives a weekly digest email: *"Risk forecast updated — 2 epics changed status."*

**Flow:**
1. Email shows: Epic "Checkout v2" likelihood-to-land moved from 78% → 52%.
2. Raj clicks through to a forecast detail view.
3. Causal explanation: *"Team Beta's PR review time has increased 60% over 3 sprints; 4 dependent stories on this epic are awaiting their reviews."*
4. Raj asks: *"What if Team Beta added one reviewer?"* (V2 feature; in MVP he sees the suggested mitigation as static recommendation)
5. Raj escalates to Beta's EM with the specific data.

**Outcome:** Slippage caught 4 weeks early. Action is mechanical (add a reviewer), not political.

**Success indicator:** ≥ 40% of slipped epics had a risk signal raised ≥ 2 sprints before slippage.

---

## UC-03 — Executive Board Prep

**Persona:** VPE-01 (Priya)
**Frequency:** Quarterly + monthly snapshots
**Priority:** P1 (MVP-lite, full version V1.5)

**Goal:** Generate a portfolio-level narrative for board reporting in under 15 minutes.

**Trigger:** Priya is preparing for a Friday board meeting.

**Flow:**
1. Priya asks: *"Give me a Q2 engineering health summary with top 3 wins and top 3 risks."*
2. The system returns a multi-paragraph narrative with embedded charts and evidence citations.
3. She refines: *"Quantify the velocity improvement in the Platform org."*
4. Response: *"Platform org throughput +18% QoQ, driven primarily by reduced PR review time (median 2.1 days → 0.9 days)."*
5. Priya copies the narrative + charts directly into her deck.

**Outcome:** Board prep time drops from 4 hours to 30 minutes. Narrative is consistent and defensible.

**Success indicator:** Self-reported reduction in board/exec prep time ≥ 50%.

---

## UC-04 — Root Cause Investigation

**Persona:** TL-01 (Alex), EM-01 (Maya)
**Frequency:** End of every sprint
**Priority:** P0 (MVP)

**Goal:** Diagnose why a sprint missed its commitment.

**Trigger:** End-of-sprint retro Friday.

**Flow:**
1. Alex asks: *"Why did Sprint 46 miss commitment by 30%?"*
2. The system returns a structured causal breakdown: scope creep (+14%), unplanned production incidents (–11%), PR review wait (–8%).
3. Alex clicks "scope creep" → shows the 3 stories added mid-sprint and who added them.
4. Alex asks: *"Compare this sprint's flow to Sprint 45."*
5. Side-by-side: Sprint 46 had 2x more context-switches per engineer.

**Outcome:** Retro discussion is grounded in specifics. The team agrees to a mid-sprint scope-change policy.

**Success indicator:** ≥ 60% of teams use the product as the primary data source in retros within 3 months of adoption.

---

## UC-05 — Proactive Burnout & Risk Detection

**Persona:** EM-01 (Maya)
**Frequency:** Continuous (alerted as detected)
**Priority:** P2 (V2 — strict access controls required)

**Goal:** Identify burnout risk before it becomes attrition.

**Trigger:** The system surfaces a proactive insight in Maya's weekly digest.

**Flow:**
1. Insight: *"Engineer J has worked >50 hrs/week for 4 consecutive weeks, with 35% of commits after 9 PM."*
2. Maya asks: *"What is J working on?"*
3. Response: J is the sole owner of 3 critical-path stories on a high-pressure epic.
4. Maya asks: *"Who else could pair with J?"*
5. The system suggests 2 engineers with skill overlap and current capacity.

**Outcome:** Maya redistributes load and addresses burnout in her next 1:1 — before J considers leaving.

**Constraint:** Individual-level signals are visible only to the engineer's direct manager-of-record. They are never aggregated into leaderboards or shared upward.

**Success indicator:** Detected burnout patterns precede actual attrition in ≥ 50% of cases (lagging indicator).

---

## UC-06 — Ad-Hoc Natural Language Query

**Persona:** All
**Frequency:** Continuous
**Priority:** P0 (MVP)

**Goal:** Answer a one-off question about delivery data without navigating dashboards.

**Trigger:** User has a specific question prompted by Slack discussion, standup, or stakeholder ask.

**Flow:**
1. User opens chat interface, types: *"Which PRs from Team Atlas have been waiting for review longer than 3 days?"*
2. The system returns a structured answer with a clickable list of PRs, reviewer assignments, and aging.
3. Each item links to GitHub.
4. User asks a follow-up: *"How does this compare to last sprint?"*
5. System maintains conversation context and answers comparatively.

**Outcome:** User gets answer in < 30 seconds vs. ~5 minutes navigating GitHub + Jira manually.

**Success indicator:** ≥ 5 queries per weekly active user per week at MVP.

---

## UC-07 — Onboarding a New Team

**Persona:** Admin (typically VPE-01 delegate, EM-01)
**Frequency:** One-time per team
**Priority:** P0 (MVP)

**Goal:** Connect a new team's data sources and grant access to team members.

**Trigger:** New squad is formed, or new customer is being onboarded.

**Flow:**
1. Admin opens the admin panel and creates a new team.
2. Selects the relevant Jira projects, GitHub repos, and members.
3. Maps identities across Jira and GitHub (auto-suggested by email; admin confirms).
4. Sets RBAC: who is the EM, who can see what.
5. Initial data backfill runs (60 days of history).
6. Admin gets a notification when the team is ready.

**Outcome:** New team is onboarded and productive in the product within 30 minutes.

**Success indicator:** Median onboarding time per team ≤ 30 minutes; ≥ 95% of identity mappings auto-resolve correctly.

---

## Use case priority matrix

| Use Case | Persona | Priority | Phase |
|---|---|---|---|
| UC-01 — Monday sprint health | EM | P0 | MVP |
| UC-02 — Quarterly slippage prediction | TPM | P0 | MVP |
| UC-03 — Exec board prep | VPE | P1 | MVP-lite, V1.5 full |
| UC-04 — Root cause investigation | TL/EM | P0 | MVP |
| UC-05 — Burnout detection | EM | P2 | V2 |
| UC-06 — Ad-hoc NL query | All | P0 | MVP |
| UC-07 — Team onboarding | Admin | P0 | MVP |