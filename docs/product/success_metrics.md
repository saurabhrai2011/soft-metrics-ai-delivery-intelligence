# Success Metrics

How we measure whether the product is working — for users, for the business, and for the AI quality bar. Metrics are split into **leading** (early signal) and **lagging** (outcome).

---

## 1. User adoption & engagement (leading)

These tell us if users are showing up.

| Metric | MVP target | V1.1 target | V2 target |
|---|---|---|---|
| Weekly active users / licensed users | ≥ 40% | ≥ 55% | ≥ 70% |
| Avg. queries per WAU per week | ≥ 5 | ≥ 8 | ≥ 12 |
| % of users who return within 7 days of first use | ≥ 50% | ≥ 65% | ≥ 75% |
| % of EMs who view dashboard ≥ 3x/week | ≥ 30% | ≥ 45% | ≥ 60% |
| % of digest emails opened | ≥ 50% | ≥ 60% | ≥ 70% |

---

## 2. Product quality (leading)

These tell us if the product works correctly when users do show up.

| Metric | MVP target | V2 target |
|---|---|---|
| Hallucination rate (eval set, 200 questions) | ≤ 2% | ≤ 0.5% |
| Citation coverage (% of factual claims with source link) | 100% | 100% |
| Refusal rate on out-of-scope questions (adversarial eval) | ≥ 95% | ≥ 99% |
| Query P95 latency | ≤ 6s | ≤ 3s |
| Dashboard load P95 latency | ≤ 2s | ≤ 1s |
| User-reported answer-helpful rate (👍 / 👎) | ≥ 70% 👍 | ≥ 85% 👍 |
| Data freshness (source change → reflected in product) | ≤ 15 min | ≤ 5 min |

---

## 3. Business outcomes (lagging)

These tell us if the product is delivering real value.

| Metric | Target | Phase |
|---|---|---|
| Reduction in time spent on weekly status reports (self-reported) | ≥ 50% | By month 3 of customer use |
| % of delivery risks caught ≥ 2 sprints early (vs. baseline) | ≥ 40% | By month 6 of customer use |
| Net Promoter Score among EM/TPM users | ≥ 40 | By V1.1 |
| Net Promoter Score among EM/TPM users | ≥ 50 | By V2 |
| Customer retention (paid, annual) | ≥ 90% | By V2 |
| Logo expansion (new teams added per customer) | ≥ 1.5x | By V2 |

---

## 4. Operational metrics

| Metric | Target |
|---|---|
| Service uptime | ≥ 99.5% (MVP), ≥ 99.9% (V2) |
| LLM cost per query (avg) | ≤ $0.05 (MVP), ≤ $0.03 (V2) |
| Time to onboard a new team (median) | ≤ 30 minutes |
| Identity-mapping auto-resolve accuracy | ≥ 95% |
| Ingestion failure alert latency | ≤ 30 minutes |

---

## 5. Anti-metrics — what we explicitly do NOT optimize for

These are metrics we deliberately avoid pushing up, because doing so would conflict with product principles or user trust.

| Anti-metric | Why we don't chase it |
|---|---|
| **Number of dashboards built** | More dashboards is the problem we're solving, not the goal. We measure consolidation, not proliferation. |
| **Time spent in product per user** | We want users to get answers and leave, not dwell. Long sessions = product failure. |
| **Individual-engineer scoring / leaderboards** | Hard product principle: no surveillance. Building this would betray user trust. |
| **Number of metrics tracked** | Quantity is not quality. We measure whether the metrics shown are *acted on*, not how many exist. |
| **Number of integrations** | Each integration is a maintenance burden. We add only those with proven user demand. |

---

## 6. Metric ownership

Clear ownership prevents metrics from becoming theatre.

| Metric category | Owner |
|---|---|
| User adoption & engagement | Product Manager |
| Product quality (LLM evals, latency) | Engineering Lead |
| Business outcomes (NPS, retention) | Product Manager + Sales/CS |
| Operational metrics | Engineering Lead |
| Anti-metrics enforcement | Product Manager (defends scope against feature creep) |

---

## 7. How metrics are reviewed

- **Weekly:** Engagement and quality metrics reviewed by PM + Eng Lead. Hallucination eval results posted in team Slack.
- **Monthly:** Business outcome review with leadership. NPS samples reviewed.
- **Quarterly:** Anti-metric review — are we accidentally optimizing for something we shouldn't be?
- **Per release:** LLM eval suite must pass before any code touching prompts ships to production.

---

## 8. Definition of "MVP success"

The MVP is considered successful if **all four** of these are true 90 days post-launch with 3 design-partner teams:

1. ≥ 40% of licensed users are weekly active.
2. Hallucination rate ≤ 2%; citation coverage = 100%.
3. ≥ 70% 👍 user-reported answer-helpfulness rate.
4. At least one design partner reports ≥ 50% reduction in status-report time.

If any of these fail, we do not move to V1.1 — we iterate on MVP first.