# System Architecture

This document describes the technical architecture of the Software Metrics AI Delivery Intelligence platform. It is intended for engineers building on the system, and for technical reviewers (engineering managers, staff engineers, AI product leads) evaluating the design.

**Status:** Draft v1.0
**Audience:** Engineers, EMs, technical interviewers

---

## Table of Contents

1. [Architecture Principles](#1-architecture-principles)
2. [System Overview](#2-system-overview)
3. [Data Ingestion Layer](#3-data-ingestion-layer)
4. [Data Model & Storage](#4-data-model--storage)
5. [Metrics Computation Layer](#5-metrics-computation-layer)
6. [RAG Pipeline](#6-rag-pipeline)
7. [LLM Layer & Prompt Management](#7-llm-layer--prompt-management)
8. [Eval Harness](#8-eval-harness)
9. [API & Application Layer](#9-api--application-layer)
10. [Security & Access Control](#10-security--access-control)
11. [Observability](#11-observability)
12. [Deployment Architecture](#12-deployment-architecture)
13. [Key Design Trade-offs](#13-key-design-trade-offs)

---

## 1. Architecture Principles

These principles guide every design decision below. When trade-offs arise, we resolve them by referring back to these.

1. **Grounding before generation.** The LLM never speaks without evidence. Every factual claim is traceable to a source row, ticket, or PR. If we can't cite it, we don't say it.
2. **Structured data first, unstructured second.** Metrics come from SQL over a structured warehouse — not from the LLM. The LLM's job is to translate questions into queries and explain results, not to compute numbers.
3. **Quality gates as code.** Eval suites run in CI on every prompt change. Hallucination rate is a release blocker, not a metric we monitor passively.
4. **Provider abstraction.** No business logic depends on a specific LLM vendor. We can swap Anthropic, OpenAI, or self-hosted models behind a single interface.
5. **Defense in depth on permissions.** RBAC is enforced at the query layer, again at the retrieval layer, and one more time when constructing LLM context. A bug in one layer doesn't leak data.
6. **Observable by default.** Every LLM call, every retrieval, every metric computation is traced. Debugging an AI product without tracing is impossible.

---

## 2. System Overview

### 2.1 Logical components

```
                    ┌────────────────────────────────────────────────────┐
                    │                   Web App (React)                  │
                    │       Dashboards · Chat UI · Admin Console         │
                    └──────────────────────────┬─────────────────────────┘
                                               │ HTTPS (REST + SSE)
                    ┌──────────────────────────▼─────────────────────────┐
                    │                  API Gateway (FastAPI)             │
                    │       AuthN/AuthZ · Rate limit · Request routing   │
                    └────┬──────────────┬───────────────┬────────────────┘
                         │              │               │
        ┌────────────────▼─┐   ┌────────▼────────┐   ┌─▼─────────────────┐
        │  Metrics Service │   │   Chat Service  │   │  Admin Service    │
        │   (read-only)    │   │   (RAG + LLM)   │   │  (config, RBAC)   │
        └────────┬─────────┘   └────┬────────────┘   └────────┬──────────┘
                 │                  │                         │
                 │     ┌────────────▼────────────┐            │
                 │     │     LLM Provider Layer  │            │
                 │     │  (Anthropic / OpenAI /  │            │
                 │     │   self-hosted adapter)  │            │
                 │     └─────────────────────────┘            │
                 │                                            │
        ┌────────▼────────────────────────────────────────────▼──────────┐
        │                  Data Warehouse (Postgres + DuckDB)            │
        │   Issues · PRs · Sprints · Metrics · Embeddings · Audit Log    │
        └────────▲───────────────────────────────────────────────────────┘
                 │
        ┌────────┴─────────────────────────────────────────────┐
        │              Ingestion Workers (Celery)              │
        │     Jira Connector · GitHub Connector · Identity     │
        └────────▲─────────────────────────────────────────────┘
                 │
        ┌────────┴─────────────────────┐
        │   External Sources (read)    │
        │   Jira API · GitHub GraphQL  │
        └──────────────────────────────┘
```

### 2.2 Service responsibilities

| Service | Responsibility | Tech |
|---|---|---|
| **Web App** | Dashboards, chat UI, admin UI | React, TypeScript, TanStack Query |
| **API Gateway** | AuthN/Z, rate limiting, request routing | FastAPI, Pydantic |
| **Metrics Service** | Compute & serve precomputed metrics | Python, SQLAlchemy, DuckDB |
| **Chat Service** | RAG orchestration, LLM calls, citation building | Python, async I/O |
| **Admin Service** | Source config, identity mapping, RBAC management | Python, FastAPI |
| **Ingestion Workers** | Pull from Jira/GitHub, normalize, write warehouse | Celery, Redis broker |
| **LLM Provider Layer** | Provider-agnostic interface for completions, embeddings | Python (custom adapter) |
| **Data Warehouse** | Source of truth for entities, metrics, embeddings | Postgres (OLTP), DuckDB (OLAP) |

### 2.3 Why these technology choices

- **Postgres + DuckDB instead of Snowflake/BigQuery.** MVP is single-tenant; cloud warehouse is overkill. DuckDB gives us fast OLAP locally; Postgres handles transactional state. Easy migration path to Snowflake/Databricks at V1.5.
- **FastAPI over Django/Flask.** Async-native (critical for LLM calls), Pydantic for type safety, OpenAPI for free.
- **Celery over plain async.** Ingestion needs reliable retries, scheduling, and back-pressure. Celery is boring and works.
- **React over server-rendered.** Chat UI needs streaming responses (SSE/WebSocket); React handles this cleanly.

---

## 3. Data Ingestion Layer

### 3.1 Connector pattern

Each external source has a connector with a uniform interface:

```python
class BaseConnector(ABC):
    @abstractmethod
    async def initial_backfill(self, since: datetime) -> AsyncIterator[Record]: ...

    @abstractmethod
    async def incremental_pull(self, cursor: Cursor) -> AsyncIterator[Record]: ...

    @abstractmethod
    def normalize(self, raw: dict) -> NormalizedRecord: ...
```

**Connectors implemented for MVP:**
- `JiraConnector` — REST API v3, polls every 15 min using `updated >= cursor`
- `GitHubConnector` — GraphQL API, polls every 15 min using `updatedAt` cursors per repo

### 3.2 Ingestion flow

```
[External API] → [Connector.pull] → [Validator] → [Normalizer] → [Identity Resolver] → [Warehouse Writer]
                                                                          │
                                                                          ▼
                                                              [Metrics Recompute Trigger]
```

1. **Pull.** Connector fetches changed records since the last cursor.
2. **Validate.** Schema validation against expected source format. Bad records → quarantine table, alert admin.
3. **Normalize.** Source-specific fields → canonical schema (see §4).
4. **Identity resolve.** Map source-specific user IDs to canonical `person_id` (see §3.3).
5. **Write.** Upsert to warehouse with source-cursor metadata for idempotency.
6. **Trigger recompute.** Notify metrics layer that affected entities have changed.

### 3.3 Identity resolution

Mapping `jira_user_id` ↔ `github_login` ↔ `email` is the hardest unsolved problem in eng-intelligence products. Our approach:

1. **Auto-resolve by email** — if Jira user email matches GitHub user public email, map automatically.
2. **Admin override** — admin UI lets the customer fix mismatches manually.
3. **Confidence score** — every mapping has `auto | admin_confirmed | unresolved` status; metrics for unresolved users are aggregated separately (not silently dropped).
4. **Audit trail** — all mapping changes logged for compliance.

**Failure mode handled:** an engineer changes their GitHub email; we don't silently lose their data. Unresolved records flow to a "review" queue surfaced in admin UI.

### 3.4 Idempotency and replay

- Every record carries `source_id` + `source_updated_at`. Re-pulling the same record is a no-op upsert.
- A full backfill can be triggered from admin UI without data corruption.
- Cursor state is stored in Postgres, not in worker memory — workers are stateless and restartable.

---

## 4. Data Model & Storage

### 4.1 Canonical entities

```
Organization (1) ──┬── (N) Team
                   │
                   └── (N) Person
                           │
                           ├── (N) Issue (via assignee)
                           └── (N) PullRequest (via author)

Team (1) ──┬── (N) Sprint
           ├── (N) Issue (via team_id)
           └── (N) Repo  (via team_id) ── (N) PullRequest

Issue (1) ──── (N) IssueChangelog   (state transitions)
PullRequest (1) ──── (N) PRReview · (N) PRComment
```

### 4.2 Why this schema

- **Team-centric, not project-centric.** Teams persist; projects come and go. Anchoring metrics on teams means re-orgs don't destroy historical data.
- **Changelog tables, not just current state.** Cycle time, time-in-status, and flow metrics require state-transition history. We store every transition with a timestamp.
- **Person, not user.** A person can have multiple identities (Jira + GitHub + email). The `Person` entity is the canonical join point.

### 4.3 Storage split

| Data | Store | Rationale |
|---|---|---|
| Entities (issues, PRs, persons, teams) | Postgres | Transactional, relational, frequent updates |
| Precomputed metrics | DuckDB (Parquet on disk) | Fast aggregation queries, columnar |
| Embeddings (for RAG) | Postgres + pgvector | Co-located with entities; pgvector handles MVP scale |
| Audit log | Postgres (append-only table) | Strong durability requirements |
| LLM trace logs | Object storage (S3 / equivalent) | High volume, cheap storage, infrequent access |

**At V1.5 scale**, embeddings move to a dedicated vector store (Pinecone, Qdrant, or Weaviate). pgvector is fine for <10M vectors.

---

## 5. Metrics Computation Layer

### 5.1 Why precomputed, not on-demand

Two reasons:

1. **Latency.** Computing cycle time over 6 months of data on a cold query is too slow for a P95 ≤ 2s dashboard.
2. **Determinism.** When the LLM cites "cycle time = 4.2 days," that number must match what the dashboard shows. Computing it twice with two code paths is a recipe for divergence.

**Single source of truth:** all metrics are computed by a single set of SQL views in DuckDB. Both the dashboard and the LLM read from these views. No metric is ever computed inline by the LLM.

### 5.2 Metric definitions

Every metric has a versioned, code-reviewed definition file:

```yaml
# metrics/cycle_time.yaml
id: cycle_time
version: 2
description: "Median time from 'In Progress' to 'Done' for completed issues"
unit: days
sql: |
  SELECT
    team_id,
    DATE_TRUNC('week', resolved_at) AS week,
    MEDIAN(EXTRACT(EPOCH FROM (resolved_at - in_progress_at)) / 86400) AS value
  FROM issue_changelog_view
  WHERE state = 'Done'
  GROUP BY team_id, week
caveats:
  - "Excludes issues that skip 'In Progress' state"
  - "Outliers (>30 days) clipped at 95th percentile"
```

**Why YAML files instead of code?** Metric definitions are reviewed by PMs and EMs, not just engineers. YAML is reviewable; raw SQL in Python is not.

### 5.3 Metric refresh strategy

- **Incremental refresh** — affected metrics recomputed when source data changes.
- **Scheduled full refresh** — nightly, to catch any drift.
- **On-demand refresh** — admin UI button for "force recompute" after config changes.

---

## 6. RAG Pipeline

This is the core AI differentiator. Most "chat with your data" products fail here by retrieving documents and asking the LLM to compute metrics. We don't.

### 6.1 Pipeline overview

```
User Question
     │
     ▼
[1. Question Classifier]──→ "metric" | "lookup" | "narrative" | "out_of_scope"
     │
     ▼
[2. Permission Filter]  ── reject if user lacks access to scope
     │
     ▼
[3. Query Planner]      ── translate question → structured query plan
     │
     ▼
[4. Retrieval]
     ├── Structured: SQL over metrics views ──┐
     ├── Semantic: vector search over text ───┤
     └── Hybrid: both, merged by relevance ───┤
                                              │
     ▼                                        │
[5. Context Builder]  ←─ retrieval results ───┘
     │   (assembles evidence with citation IDs)
     ▼
[6. Answer Generator (LLM)]
     │   (prompt enforces: cite every fact, refuse if no evidence)
     ▼
[7. Citation Validator]
     │   (every claim must reference a retrieval ID; else mark low-confidence)
     ▼
[8. Streamed Response]  → user sees answer + evidence panel
```

### 6.2 Step-by-step

**Step 1 — Question classifier.** A small, fast LLM call (or fine-tuned classifier) routes the question:
- *"What was Team Atlas's velocity last sprint?"* → `metric`
- *"Which PRs has Maya reviewed this week?"* → `lookup`
- *"Why did Sprint 46 miss commitment?"* → `narrative`
- *"What's the meaning of life?"* → `out_of_scope` → polite refusal

**Step 2 — Permission filter.** Before any retrieval, we determine which teams/scopes the user can see. This becomes a `WHERE team_id IN (...)` filter applied to all subsequent queries. **No retrieval ever returns data outside this scope.**

**Step 3 — Query planner.** For metric/lookup questions, an LLM call produces a structured query plan:

```json
{
  "intent": "metric",
  "metric_id": "cycle_time",
  "scope": {"team_id": "atlas"},
  "time_range": "last_sprint",
  "comparison": "previous_sprint"
}
```

The plan is validated against a schema. If validation fails, we refuse rather than guess.

**Step 4 — Retrieval.** Three modes, used alone or combined:
- **Structured (SQL)** — for metric questions, run the validated plan against precomputed metric views.
- **Semantic (vector)** — for lookup/narrative, embed the question and retrieve top-k issues/PRs/comments by cosine similarity.
- **Hybrid** — for narrative questions ("why did velocity drop"), combine metric SQL results with relevant ticket/PR text.

**Step 5 — Context builder.** Assemble retrieved evidence into a compact context block, each item tagged with a citation ID:

```
[E1] Issue ATLAS-1234: "Login flow redesign" — cycle time 8.2 days, 3.5x team median
[E2] PR #2341 in atlas-web: opened 2026-04-15, awaiting review from @mike
[E3] Sprint 46 metric: planned 28 points, delivered 19 points (–32%)
```

**Step 6 — Answer generation.** The LLM receives:
- The user's question
- The evidence block with citation IDs
- A system prompt that enforces: *"Every factual claim must cite at least one [E#]. If evidence is insufficient, say so. Never invent numbers."*

**Step 7 — Citation validator.** A deterministic post-processor checks that every claim in the answer references a valid [E#]. Claims without citations are flagged. If >10% of claims lack citations, the answer is rejected and we either retry or surface "low confidence" to the user.

**Step 8 — Streaming.** The validated answer streams back via Server-Sent Events; the evidence panel renders alongside.

### 6.3 Why this is better than naive RAG

| Naive RAG | This system |
|---|---|
| LLM computes metrics from retrieved text | Metrics come from precomputed SQL; LLM only narrates |
| Permissions checked at UI layer | Permissions enforced at retrieval layer (defense in depth) |
| Citations are decorative | Citations are validated; uncited claims get flagged |
| One retrieval mode | Hybrid retrieval matched to question type |
| Works on a demo, fails in production | Works on production-grade questions |

### 6.4 What can still go wrong

- **Query planner hallucinates a metric_id.** Mitigation: schema validation rejects unknown metrics; eval suite includes adversarial questions targeting fake metrics.
- **Retrieval misses the right document.** Mitigation: hybrid retrieval, eval set tracks recall@k.
- **LLM ignores the citation requirement.** Mitigation: citation validator catches it; eval suite measures citation coverage as a gate.
- **Retrieved evidence is stale.** Mitigation: every retrieval result includes a freshness timestamp shown in the UI.

---

## 7. LLM Layer & Prompt Management

### 7.1 Provider abstraction

```python
class LLMProvider(Protocol):
    async def complete(
        self,
        prompt: Prompt,
        model: ModelTier,        # "fast" | "smart" | "reasoning"
        max_tokens: int,
        temperature: float,
    ) -> Completion: ...

    async def embed(self, texts: list[str]) -> list[list[float]]: ...
```

Implementations: `AnthropicProvider`, `OpenAIProvider`, `SelfHostedProvider`. The rest of the system depends only on the protocol.

**Why three model tiers?**
- `fast` (e.g., Haiku-class) — for question classification, cheap routing
- `smart` (e.g., Sonnet-class) — for query planning, answer generation
- `reasoning` (e.g., Opus-class) — for V2 narrative reports, complex root cause analysis

Mixing tiers reduces cost by ~70% vs. always using the largest model.

### 7.2 Prompt management

Prompts are code. They live in `prompts/` as versioned files:

```
prompts/
  classifier_v3.txt
  query_planner_v5.txt
  answer_generator_v7.txt
  retro_narrative_v1.txt
```

Rules:
- Every prompt has a version suffix and changelog entry.
- Prompt changes go through code review like any other code.
- The eval suite runs against the new prompt before merge.
- Old versions are kept; we can A/B test versions in production.

### 7.3 Cost & rate-limit management

- **Caching** — identical question + context pairs cached for 1 hour (hash of normalized inputs).
- **Per-user budgets** — soft cap of 100 queries/user/day; hard cap of 500.
- **Provider fallback** — if primary provider is rate-limited, fall back to secondary (graceful degradation, not silent failure — user sees a "using backup model" indicator).

---

## 8. Eval Harness

The eval harness is the single most important piece of infrastructure for a trustworthy AI product. Without it, prompt changes are gambling.

### 8.1 What we eval

| Eval suite | What it measures | Gate? |
|---|---|---|
| **Hallucination eval** | Factual accuracy vs. ground truth | Yes — release blocker |
| **Citation eval** | % of factual claims with valid citation | Yes — release blocker |
| **Refusal eval** | Correctly refuses out-of-scope/adversarial questions | Yes — release blocker |
| **Permission eval** | Never returns data outside user's scope | Yes — release blocker (security) |
| **Latency eval** | P95 latency on representative question set | Yes — perf regression blocker |
| **Helpfulness eval** | LLM-as-judge rates answer helpfulness | Tracked, not blocking |
| **Cost eval** | Average cost per query in eval set | Tracked, alerts on regression |

### 8.2 Eval set construction

The eval set is a versioned collection of question/answer/context tuples:

```yaml
# evals/sets/mvp_v1/EM-001.yaml
id: EM-001
persona: EM-01
question: "What was Team Atlas's velocity last sprint?"
scope:
  user_id: u_maya
  team_access: [atlas]
fixtures:
  - sprint_46_atlas.json
expected:
  must_contain:
    - metric: cycle_time
    - team: atlas
  must_cite_evidence: true
  must_not_contain:
    - data_from_team: beta  # permission test
  acceptable_answers_regex:
    - "(?i)velocity.*Sprint 46.*([0-9]+)\\s*(points|story points)"
```

### 8.3 How evals run

- **On every PR** that touches `prompts/`, `chat_service/`, or `rag_pipeline/` — eval suite runs in CI.
- **Nightly** — full suite (slow + adversarial) runs on `main`.
- **Pre-release** — manual signoff on eval dashboard before deploying to production.

### 8.4 Adversarial eval set

A separate eval set deliberately tries to break the system:

- Questions about teams the user can't access → must refuse, must not leak any signal of existence.
- Questions about non-existent metrics → must refuse, not hallucinate a number.
- Prompt injection attempts in ticket descriptions → must not change behavior.
- Questions designed to elicit individual-engineer comparisons → must refuse per product principle.
- Out-of-scope questions ("write me a poem") → polite refusal.

Adversarial eval is run on every release. A regression here is a security/trust incident, not a product issue.

### 8.5 LLM-as-judge for helpfulness

For helpfulness scoring, we use a separate LLM (different provider from the answering model) as a judge. The judge sees the question, the answer, and the ground-truth context, and rates 1–5. We track median and bottom-decile scores.

**Caveat acknowledged:** LLM-as-judge has known biases (length bias, position bias, self-preference). We calibrate against human-labeled samples quarterly.

---

## 9. API & Application Layer

### 9.1 Core endpoints

```
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/teams                          # scoped to user permissions
GET    /api/v1/teams/{team_id}/dashboard
GET    /api/v1/teams/{team_id}/metrics?metric=cycle_time&range=last_30d
POST   /api/v1/chat/sessions                  # create chat session
POST   /api/v1/chat/sessions/{id}/messages    # send question, stream response
GET    /api/v1/chat/sessions/{id}/messages    # history
POST   /api/v1/admin/sources                  # admin only
PATCH  /api/v1/admin/identities/{person_id}
GET    /api/v1/admin/audit_log                # admin only
```

### 9.2 Streaming

Chat responses use Server-Sent Events. The client receives:
1. `metadata` event — query plan, retrieval results, evidence list
2. `token` events — answer text streaming in
3. `citation` events — citation IDs as they're emitted
4. `done` event — final validation result, helpfulness prompt

### 9.3 Frontend

- **State:** TanStack Query for server state, Zustand for UI state.
- **Charts:** Recharts for metrics dashboards, custom SVG for traffic-light health summary.
- **Chat:** custom component with streamed token rendering, click-through citation panel.

---

## 10. Security & Access Control

### 10.1 Defense in depth

Permissions are enforced in three places — by design, not by accident:

1. **API Gateway** — coarse-grained: is the user authenticated?
2. **Service layer** — fine-grained: does this user have access to this team?
3. **Retrieval layer** — every SQL query and vector search is scoped to the user's permitted team IDs.

A bug in any one layer doesn't leak data, because the next layer also enforces.

### 10.2 RBAC model

```
User
  ├── role: "admin" | "manager" | "member"
  └── team_memberships: [
        { team_id: "atlas", relationship: "ic" },
        { team_id: "platform", relationship: "manager" },
      ]

Permission rules:
  - member sees: their team(s)' aggregated metrics + their own individual data
  - manager sees: above + individual data of their direct reports
  - admin sees: all teams' aggregated metrics; individual data still requires manager-of-record relationship
```

### 10.3 LLM data handling

- LLM context is constructed only from data the user has permission to see.
- No customer data is sent to LLM providers without a zero-data-retention agreement.
- Prompt injection from ingested data (e.g., a Jira ticket description containing "ignore previous instructions") is neutralized by:
  - Wrapping all retrieved data in clearly-delimited tags
  - Instructing the model that text inside data tags is data, not instructions
  - Adversarial eval set explicitly tests injection attempts

### 10.4 Audit log

Every action that affects access or surfaces individual-level data is logged:
- User login/logout
- Permission changes
- Identity mapping changes
- Individual-level metric drill-ins (per the no-surveillance principle, these are auditable)

---

## 11. Observability

### 11.1 What we trace

Every request gets a trace ID. For chat requests, the trace includes:
- Question classification result + latency
- Permission filter decisions
- Query plan (the structured JSON)
- Retrieval results (IDs only, not content, in trace)
- LLM provider, model, prompt version, token counts, latency, cost
- Citation validator results
- Final response length, streaming time

### 11.2 Tooling

- **Tracing:** OpenTelemetry, exported to whatever the customer uses (Jaeger, Datadog, Honeycomb).
- **Metrics:** Prometheus-compatible, scraped by `/metrics` endpoint.
- **Logs:** Structured JSON, shipped via standard log aggregation.

### 11.3 Why this matters for AI products specifically

AI products fail in subtle ways. A traditional service either returns 200 or 500. An AI service can return 200 with a wrong answer, a low-confidence answer, or a hallucinated citation. Without rich tracing, you can't tell these apart in production. We treat this as table stakes.

---

## 12. Deployment Architecture

### 12.1 MVP — single-tenant, self-hosted

```
[Customer VPC]
  ├── App Server (Docker Compose or single ECS task)
  │   ├── api-gateway
  │   ├── metrics-service
  │   ├── chat-service
  │   └── admin-service
  ├── Worker Nodes (ECS or autoscaling group)
  │   └── celery-workers
  ├── Postgres (RDS or managed equivalent)
  ├── Redis (ElastiCache)
  └── Egress allowlist:
        - Customer's Jira instance
        - Customer's GitHub
        - LLM provider endpoint
```

### 12.2 V1.5 — multi-tenant SaaS

- Postgres per-tenant schema isolation
- Shared compute, tenant-scoped at every query
- Per-tenant rate limits and budget enforcement
- SOC 2 Type I / II controls

### 12.3 Why single-tenant first

Most enterprise eng-data buyers will not allow their Jira/GitHub data into a multi-tenant cloud SaaS in the first 12 months. Single-tenant first lets us land design-partner customers and learn before building multi-tenancy. Multi-tenancy is added at V1.5 as a deliberate, separate workstream — not as an afterthought.

---

## 13. Key Design Trade-offs

These are the decisions that took the longest to make. Each is recorded as an ADR (Architecture Decision Record) in `decisions/`.

| Trade-off | Choice | Reasoning |
|---|---|---|
| **Compute metrics with LLM vs. SQL** | SQL | Determinism. Same number must appear in dashboard and chat. |
| **Single LLM provider vs. abstraction** | Abstraction | Avoid lock-in, enable eval comparison, hedge against pricing changes. |
| **pgvector vs. dedicated vector DB** | pgvector for MVP | Operational simplicity. Move to dedicated store at V1.5. |
| **Postgres + DuckDB vs. cloud warehouse** | Postgres + DuckDB | Cost and simplicity at MVP scale. |
| **Streaming vs. batched LLM responses** | Streaming | Latency perception matters; first-token-time is what users feel. |
| **Single-tenant vs. multi-tenant MVP** | Single-tenant | Enterprise data sensitivity; faster path to design-partner GA. |
| **Eval-as-CI-gate vs. monitoring only** | CI gate | Quality regressions caught before users see them. |
| **Aggregate vs. individual-level metrics** | Aggregate by default | Anti-surveillance product principle; individual data behind manager-of-record. |

---

## Appendix — What this architecture explicitly does NOT do

For clarity, here are anti-patterns we've consciously avoided:

- **No "let the LLM SQL query the database directly"** — too easy to leak permissions, hallucinate joins, or rack up cost.
- **No "vector search alone for everything"** — semantic search can't answer "what was velocity last sprint" reliably.
- **No fine-tuned model for narration** — base models are good enough; fine-tuning adds operational burden without proportional gain at this stage.
- **No agent loops for MVP** — multi-step agents are powerful but unreliable. We'll revisit at V2 with proper tool-use scaffolding.
- **No real-time WebSocket sync of dashboard data** — 15-minute freshness is the SLA; users don't need second-by-second updates and we shouldn't promise them.

---

## References to other docs

- **`personas.md`** — who this system is built for
- **`use_cases.md`** — what scenarios drive these design choices
- **`product_requirements.md`** — FR/NFR IDs traced to architecture components
- **`roadmap.md`** — phases align with architecture maturity (single-tenant → multi-tenant → predictive)
- **`success_metrics.md`** — what "working" means for this system