# Seeded patterns in synthetic data

These are the patterns the agent should be able to surface.
They are also the source of truth for the eval golden set.

1. **Silent slip — Network Modernization.** All Capabilities under
   INIT-003 ("Network Modernization") run 30% longer than planned.
   Visible by comparing planned_end_date vs actual_end_date at the
   Capability level, grouped by initiative.

2. **Defect outlier — Team Phoenix.** Defect count is 2x other teams.
   Visible by group-by team at the Epic level.

3. **Stuck Capability — API Gateway Replatform.** 60% of its Epics are
   stuck in "In Review" status for >14 days. Visible by filtering
   Epics where capability_id = <id> and status = 'In Review' and
   days_in_current_status > 14.

4. **Q3 seasonal slowdown.** Average cycle_time_days is 25% higher
   for Epics with start_date in July–September.

These four patterns power 8 of the 30 golden eval questions in
evals/golden.jsonl. The other 22 are control / refusal / multi-step
cases.