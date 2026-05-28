# Software Metrics AI Delivery Intelligence

AI-powered delivery intelligence assistant that transforms software metrics into conversational insights, executive narratives, root cause analysis, and predictive signals.

## Repository Structure

- `/docs` — product, architecture, and delivery documentation
- `/product` — PRD, roadmap, backlog, release plan
- `/design` — wireframes, prototypes, design prompts, handoff assets
- `/data` — sample CSV, synthetic Initiative/Capability/Epic dataset, and `ground_truth.md` describing seeded patterns
- `/src` — application, agents, pipelines, retrieval, observability
- `/scripts` — synthetic data generator and eval runner
- `/evals` — golden questions and scorecards
- `/infra` — database, deployment, and Docker assets
- `/tests` — unit, integration, and evaluation tests
- `/demo` — screenshots, walkthrough script, and sample questions
- `/.github/workflows` — PR-gated CI for golden evals

## Current implementation

What is actually built and running today:

- **Synthetic delivery dataset** (`data/synthetic/`) — Initiatives → Capabilities → Epics with four seeded patterns (silent slip, defect outlier, stuck capability, Q3 seasonal slowdown); pattern intent documented in `data/ground_truth.md`.
- **Streamlit dashboard** (`src/app/frontend/streamlit_app.py`) — KPI tiles, one table per seeded pattern with inline progress bars (`st.column_config.ProgressColumn`), and an agent Q&A panel with loading state.
- **Pandas metrics service** (`src/services/metrics_service.py`) — headline KPIs and per-pattern aggregates over the synthetic data; powers the dashboard.
- **Claude tool-calling agent** (`src/agents/orchestrator.py`) — Anthropic Sonnet/Opus driven; picks tools, accumulates evidence, returns a cited answer plus a trace.
- **DuckDB-backed SQL tool** (`src/agents/tools/query_metrics.py`) — read-only SELECT against the synthetic dataset; the agent's primary analytical path.
- **Secondary agent tools** — RCA, risk, narrative, and metrics-explainer wrappers around the metrics service (`src/agents/tools/`).
- **Citation validator** (`src/rag/citation_validator.py`) — checks every cited evidence ID resolves to a tool result.
- **Golden eval set** (`evals/golden.jsonl`, 5 questions) and **eval runner** (`scripts/run_evals.py`) with five mechanical checks: tool match, entity recall, phrase recall, citation validity, refusal guard. Scorecards written to `evals/scorecards/`.
- **PR-gated CI** (`.github/workflows/evals.yml`) — runs the golden eval set on every pull request; the `ANTHROPIC_API_KEY` is scoped to a GitHub Environment requiring manual reviewer approval before injection.

## Data model

```
initiatives  (initiative_id, initiative_name, owner, start_date, target_end_date, budget_aud_m, strategic_priority, status)
capabilities (capability_id, capability_name, initiative_id, owner, start_date, planned_end_date, actual_end_date, status, completion_pct)
epics        (epic_id, epic_name, capability_id, team, owner, priority, story_points, start_date, planned_end_date, actual_end_date,
              cycle_time_days, status, days_in_current_status, defect_count)
```

Joins: `capabilities.initiative_id → initiatives`, `epics.capability_id → capabilities`.

## Running locally

```bash
# Install (use a venv)
python -m venv .venv
.venv/Scripts/activate              # Windows
pip install -r requirements-evals.txt streamlit

# Set your key
cp .env.example .env                # then fill ANTHROPIC_API_KEY

# Streamlit dashboard
.venv/Scripts/streamlit.exe run src/app/frontend/streamlit_app.py
# → http://localhost:8501

# Golden evals against the live agent
python scripts/run_evals.py
python scripts/run_evals.py --only G1,G4   # subset
```

## Deferred from target architecture

Documented but not yet built:

- Postgres backing store
- FastAPI API gateway
- React frontend
- Celery ingestion workers
- Jira and GitHub connectors
- pgvector semantic retrieval
- Multi-provider LLM abstraction (current path is Anthropic-only)
- RBAC and audit logging
- OpenTelemetry tracing
