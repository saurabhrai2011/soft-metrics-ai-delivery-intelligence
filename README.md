# Software Metrics AI Delivery Intelligence

AI-powered delivery intelligence assistant that transforms software metrics into conversational insights, executive narratives, root cause analysis, and predictive signals.

## Repository Structure
/docs - product, architecture, and delivery documentation
/product - PRD, roadmap, backlog, release plan
/design - wireframes, prototypes, design prompts, handoff assets
/data - raw, processed, sample, and synthetic data
/src - application, agents, pipelines, retrieval, observability
/infra - database, deployment, and Docker assets
/tests - unit, integration, and evaluation tests
/evals - golden questions and scorecards
/demo - screenshots, walkthrough script, and sample questions

## Current MVP Implementation

This MVP implements a simplified vertical slice of the target architecture:

- CSV-based sample dataset
- Pandas-based metrics service
- Rule-based question planner
- Evidence builder with citation IDs
- Deterministic answer generator
- Citation validator
- Streamlit UI
- Basic evaluation case

## Deferred from Target Architecture

The following architecture components are documented but deferred from the MVP:

- DuckDB
- Postgres
- FastAPI API Gateway
- React frontend
- Celery ingestion workers
- Jira and GitHub connectors
- pgvector semantic retrieval
- LLM provider abstraction
- RBAC and audit logging
- OpenTelemetry tracing