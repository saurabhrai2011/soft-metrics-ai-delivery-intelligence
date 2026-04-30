# Product Requirements

This document translates the product vision into MVP scope and detailed requirements. Each requirement has a unique ID for traceability across design, engineering, and QA.

---

## 1. MVP Scope

**MVP goal:** Deliver enough value that an EM or TPM uses the product weekly instead of building manual reports — within a 4-month build cycle.

### 1.1 In scope for MVP

| Capability | Description |
|---|---|
| **Data integrations (read-only)** | Jira Cloud, GitHub, GitHub Enterprise (single org each) |
| **Core metrics** | Velocity, throughput, cycle time, PR review time, WIP, scope change, planned vs. delivered |
| **Conversational interface** | Natural-language Q&A over the metrics, scoped to single team or cross-team |
| **Grounded RAG** | Every answer cites the specific tickets, PRs, or commits used as evidence |
| **Team health dashboard** | Traffic-light summary per team with 1-sentence narrative |
| **Risk forecasting (basic)** | Probability that current sprint will hit commitment, based on burndown + historic patterns |
| **Weekly digest email** | Per-user summary with top 3 risks and 3 wins |
| **Auth & permissions** | SSO (Google + Okta), team-scoped access (no cross-team data leakage) |

### 1.2 Explicitly out of scope for MVP

- Datadog, PagerDuty, Sentry, Linear, Asana, Azure DevOps integrations *(V1.1+)*
- Counterfactual / "what-if" simulations *(V2)*
- Burnout / attrition prediction *(V2)*
- Mobile app *(V2+)*
- Custom metric definitions *(V1.1)*
- Slack/Teams bot *(V1.1)*
- Auto-generated retro decks *(V2)*
- Multi-tenant SaaS deployment — MVP is single-tenant, self-hosted reference architecture

---

## 2. Functional Requirements

Numbered for traceability. **MVP** items are required for launch; **V1.1** and **V2** are post-MVP.

### 2.1 Data ingestion

- **FR-1.1 (MVP)** — System ingests Jira issues, sprints, and changelog data via REST API, refreshed every 15 minutes.
- **FR-1.2 (MVP)** — System ingests GitHub PRs, reviews, commits, and comments via GraphQL API, refreshed every 15 minutes.
- **FR-1.3 (MVP)** — System resolves identity across Jira and GitHub by configurable email mapping; admin can override mappings.
- **FR-1.4 (V1.1)** — System ingests CI/CD pipeline data (GitHub Actions, Jenkins) for build success/failure metrics.
- **FR-1.5 (V1.1)** — System ingests incident data (PagerDuty, Opsgenie) for reliability metrics.

### 2.2 Metrics & analytics

- **FR-2.1 (MVP)** — System computes the standard DORA-adjacent metrics: deployment frequency proxy, lead time for changes, and change failure rate proxy.
- **FR-2.2 (MVP)** — System computes flow metrics: cycle time, throughput, WIP, work-item aging.
- **FR-2.3 (MVP)** — System computes sprint metrics: planned vs. delivered, scope change %, commitment reliability.
- **FR-2.4 (MVP)** — System computes PR metrics: time-to-first-review, time-to-merge, review depth (comments per PR).
- **FR-2.5 (V1.1)** — Admin can define custom metrics via a config file (no UI builder until V2).

### 2.3 Conversational interface

- **FR-3.1 (MVP)** — User can ask natural-language questions in a chat interface; answers cite specific source artifacts (Jira keys, PR numbers).
- **FR-3.2 (MVP)** — System maintains conversation context within a session (follow-up questions resolved against prior turns).
- **FR-3.3 (MVP)** — System refuses or asks for clarification when a question is ambiguous or out-of-scope, rather than hallucinating.
- **FR-3.4 (MVP)** — Every answer surfaces an "Evidence" panel listing the underlying data with click-through links.
- **FR-3.5 (V1.1)** — User can save and share answers as durable links (snapshot-in-time).
- **FR-3.6 (V2)** — Slack and Teams bot interfaces with same Q&A capability.

### 2.4 Dashboards & visualization

- **FR-4.1 (MVP)** — Team dashboard shows traffic-light health, key metrics with sparklines, and a 1-sentence AI-generated narrative.
- **FR-4.2 (MVP)** — Portfolio dashboard (for VPE persona) shows all teams with rollup health.
- **FR-4.3 (MVP)** — Each chart supports drill-in to source data (ticket list, PR list).
- **FR-4.4 (V1.1)** — Custom dashboard builder (drag-drop widgets).

### 2.5 Predictions & alerts

- **FR-5.1 (MVP)** — System predicts probability of current sprint hitting commitment, updated daily.
- **FR-5.2 (MVP)** — Weekly digest email per user summarizes top 3 risks and 3 wins for their scope.
- **FR-5.3 (V1.1)** — User can configure custom alerts (e.g., "alert me when PR review time exceeds 3 days").
- **FR-5.4 (V2)** — Counterfactual simulation: "What if we added a reviewer?"
- **FR-5.5 (V2)** — Burnout / attrition risk detection at the individual level (with strict access controls — only direct manager).

### 2.6 Admin, auth, and access control

- **FR-6.1 (MVP)** — SSO via Google Workspace and Okta (SAML 2.0).
- **FR-6.2 (MVP)** — Role-based access: Admin, Manager, Member. Members see only their team's data; Managers see their reports' teams; Admins see all.
- **FR-6.3 (MVP)** — Admin UI for configuring data sources, identity mappings, and user roles.
- **FR-6.4 (V1.1)** — Audit log of admin actions and data access.

---

## 3. Non-Functional Requirements

### 3.1 Performance

- **NFR-1.1** — Conversational query P95 latency: ≤ 6 seconds for queries over a single team's data.
- **NFR-1.2** — Dashboard load P95 latency: ≤ 2 seconds.
- **NFR-1.3** — Data freshness: ingested data reflects in dashboards within 15 minutes of source change.

### 3.2 Reliability & availability

- **NFR-2.1** — Service availability target: 99.5% during MVP, 99.9% by V2.
- **NFR-2.2** — Graceful degradation: if LLM provider is down, dashboards remain functional; only chat interface is disabled.
- **NFR-2.3** — Source data integration retries with exponential backoff; ingestion failures alert the admin within 30 minutes.

### 3.3 Security & privacy

- **NFR-3.1** — All data encrypted in transit (TLS 1.3) and at rest (AES-256).
- **NFR-3.2** — User data scoped strictly by RBAC; no LLM prompts may include data outside the requesting user's permission scope.
- **NFR-3.3** — LLM provider must be configured to not retain or train on customer data (e.g., zero data retention agreements).
- **NFR-3.4** — PII (engineer names, emails) is pseudonymized in any analytics or telemetry sent to third parties.
- **NFR-3.5** — System passes SOC 2 Type II controls by V2.

### 3.4 LLM-specific quality

- **NFR-4.1** — Hallucination rate: ≤ 2% of answers contain a factual error not traceable to source data, measured against a held-out eval set of 200 questions.
- **NFR-4.2** — Citation coverage: 100% of factual claims in chat answers cite at least one source artifact.
- **NFR-4.3** — Refusal rate on out-of-scope questions: ≥ 95% (measured on adversarial eval set).
- **NFR-4.4** — Cost per query: ≤ $0.05 average across all query types at MVP scale.

### 3.5 Scalability

- **NFR-5.1** — MVP supports up to 200 engineers and 20 teams in a single deployment.
- **NFR-5.2** — V1.1 supports up to 1,000 engineers and 100 teams.
- **NFR-5.3** — Architecture supports horizontal scaling of ingestion and query layers independently.

### 3.6 Maintainability

- **NFR-6.1** — Test coverage ≥ 75% on backend services.
- **NFR-6.2** — All LLM prompts versioned and stored as code; prompt changes require code review.
- **NFR-6.3** — Eval suite runs on every PR that touches LLM code paths.

---

## 4. Open questions & risks

### 4.1 Open questions

1. **Source-of-truth conflicts** — When Jira and GitHub disagree (e.g., PR merged but ticket still "In Progress"), which wins for metric calculation? *Proposal: configurable per-org, default to Jira for delivery state, GitHub for code state.*
2. **Privacy of individual-level signals** — How do we expose individual-level data (e.g., PR review time) to managers without enabling surveillance? *Proposal: aggregate by default, individual drill-in requires explicit "manager-of-record" relationship.*
3. **LLM provider dependency** — Single-vendor dependency is a risk. *Proposal: abstraction layer to swap providers; eval suite runs against multiple providers.*
4. **Cold start for new teams** — New teams have no historical data; how do predictions work? *Proposal: bootstrap from org-level priors for first 3 sprints.*

### 4.2 Top risks

| Risk | Impact | Mitigation |
|---|---|---|
| LLM hallucinates a metric value, leadership acts on it, trust collapses | Critical | Strict grounding + citation requirement; eval gate on every release; visible "low confidence" indicator |
| Engineers see this as surveillance and reject it | Critical | Aggregate-by-default, anti-metric principles published, individual-level data behind explicit ACLs |
| Existing tools move into conversational AI first | High | Lead with grounding/citation quality, not feature breadth; published evals as differentiator |
| Customer data integration fails for niche Jira configurations | Medium | Beta with 3 design partners covering Jira Cloud + Server + DC; fallback "manual import" path |
| Cost of LLM queries scales unfavorably | Medium | Caching layer for common queries; smaller models for routing; per-user query budgets |