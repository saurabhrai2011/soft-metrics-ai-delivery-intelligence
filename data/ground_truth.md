# Seeded patterns in synthetic data

This doc describes the *intent* behind each pattern the agent should be
able to surface — not the specific values. Numbers (slip %, defect
ratios, stuck-share %) are recomputed from the data by the eval
runner; do not hand-assert them here.

Canonical sources:
- **Data:** `scripts/generate_synthetic_data.py` (the generator IS the spec)
- **Expected answers:** `evals/golden.jsonl` (mechanically gradeable)
- **This doc:** the human-readable map of what each pattern is testing

---

## Patterns

### 1. Silent slip — Network Modernization (INIT-003)
Capabilities under INIT-003 finish meaningfully later than planned,
yet the initiative's top-line status stays "On Track."

**Why it matters:** executives miss late-stage scope creep when the
RAG status is green. The agent should surface the gap between
planned and actual completion dates even when no status field flags it.

**Where to look:** `capabilities.planned_end_date` vs
`capabilities.actual_end_date`, grouped by initiative.

### 2. Defect outlier — Team Phoenix
One team produces materially more defects per epic than peers.

**Why it matters:** team-level quality outliers warrant systemic
investigation (process, tooling, complexity) before anyone reaches
for individual performance conclusions. Tests whether the agent
quantifies the gap cleanly without naming people.

**Where to look:** `epics.defect_count` grouped by `team`.

### 3. Stuck capability — API Gateway Replatform
A meaningful share of this capability's epics has been sitting in
"In Review" status well past a reasonable threshold.

**Why it matters:** review queues are a classic hidden bottleneck —
work doesn't show as blocked, just slow. The agent should identify
the choke point by status, not assume "Blocked" is the only stuck state.

**Where to look:** `epics` filtered by `capability_id` for API Gateway
Replatform and `days_in_current_status` over the two-week threshold.

### 4. Q3 seasonal slowdown
Epics started July–September take longer to complete than work
started in other quarters.

**Why it matters:** seasonal patterns should inform capacity planning,
not be misread as a team performance issue. The agent should identify
the temporal pattern and avoid inventing a root cause not supported
by evidence.

**Where to look:** `epics.start_date` bucketed by quarter,
`AVG(cycle_time_days)`.

---

## Eval coverage

The 5 golden questions in `evals/golden.jsonl` cover all four patterns
plus a refusal/guardrail case (PIP recommendation request). The
golden set is intentionally small — high-signal, mechanically graded,
fast to re-run. Add new questions as new patterns are seeded.
