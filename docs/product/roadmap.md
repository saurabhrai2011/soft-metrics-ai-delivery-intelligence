# Roadmap

Phased delivery from MVP to V2. Estimated timeline assumes a small team (3–5 engineers, 1 PM, 1 designer). Each phase has a theme, scope, and exit criteria.

---

## Phase 0 — Foundations (Months 0–1)

**Theme:** "Get the boring stuff right before AI."

### Scope
- Project scaffolding, CI/CD, deployment pipeline
- Data model design (teams, sprints, issues, PRs, identities)
- Jira and GitHub ingestion connectors
- Identity resolution layer
- Auth: SSO (Google + Okta), RBAC skeleton
- Eval harness scaffolding (so AI features ship with quality gates from day one)

### Exit criteria
- Data ingested for one design-partner team end-to-end
- Eval harness runs on CI for every PR
- SSO + RBAC working with 3 test users

---

## Phase 1 — MVP (Months 2–4)

**Theme:** "Conversational dashboards that don't lie."

### Scope
- Core flow & sprint metrics (cycle time, throughput, WIP, planned vs. delivered)
- Team health dashboard with traffic-light + 1-sentence AI narrative
- Portfolio dashboard for VPE persona
- Conversational Q&A with grounded RAG (citations on every answer)
- Sprint commitment risk forecast (basic)
- Weekly digest email

### Exit criteria
- 3 design-partner teams using the product weekly
- Hallucination rate ≤ 2% on eval set (200 questions)
- Citation coverage = 100%
- ≥ 5 queries per WAU per week
- ≥ 70% 👍 user-reported answer-helpfulness rate

---

## Phase 2 — V1.1: Where you already work (Months 5–8)

**Theme:** "Meet users in the tools they live in."

### Scope
- Slack + Teams bot integrations (same Q&A capability)
- CI/CD ingestion (GitHub Actions, Jenkins)
- PagerDuty / incident data integration
- Custom alerts (user-configured thresholds)
- Custom metric definitions (config-as-code)
- Saveable / shareable answers (durable links)
- Audit log

### Exit criteria
- 10 paying customers
- ≥ 50% of queries originate in Slack/Teams (not the web app)
- NPS ≥ 30
- Uptime ≥ 99.5%

---

## Phase 3 — V1.5: Trust at the executive level (Months 9–11)

**Theme:** "Earn the right to be in the boardroom."

### Scope
- Portfolio-level narrative reports (auto-generated for VPE persona)
- Multi-quarter trend analysis
- Multi-tenant SaaS deployment (move off single-tenant reference architecture)
- SOC 2 Type I certification
- Datadog + Sentry integrations
- Audit log expanded for compliance use cases

### Exit criteria
- First Fortune 500 customer signed
- Multi-tenant deployment serves 10+ orgs without isolation issues
- SOC 2 Type I report issued
- ≥ 3 customers using auto-generated narratives in actual board prep

---

## Phase 4 — V2: From reactive to predictive (Months 12–18)

**Theme:** "Predict, don't just describe."

### Scope
- Counterfactual simulations ("what if we added a reviewer?")
- Burnout / attrition risk detection (with strict ACLs — manager-of-record only)
- Auto-generated retro decks
- Cross-org benchmarking (opt-in, anonymized)
- Mobile app (read-only, focus on alerts and digest)
- SOC 2 Type II certification
- LLM provider abstraction layer (swap providers without rewrites)

### Exit criteria
- 50 paying customers
- Predictive accuracy: ≥ 70% precision on 4-week-out epic slippage forecasts
- NPS ≥ 50
- Hallucination rate ≤ 0.5% on eval set
- Uptime ≥ 99.9%

---

## Roadmap visualization

```