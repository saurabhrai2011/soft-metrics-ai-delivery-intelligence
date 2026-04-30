def classify_question(question: str) -> dict:
	q = question.lower()

	if "bottleneck" in q or "wait" in q or "ready for build" in q:
		return {
			"intent": "metric",
			"metric_type": "bottleneck",
		}

	if "risk" in q or "behind" in q or "delay" in q:
		return {
			"intent": "metric",
			"metric_type": "risk",
		}

	if "commitment" in q or "reliability" in q:
		return {
			"intent": "metric",
			"metric_type": "commitment",
		}

	if "mttr" in q or "incident" in q:
		return {
			"intent": "metric",
			"metric_type": "operational_health",
		}

	if "summary" in q or "executive" in q or "health" in q:
		return {
			"intent": "narrative",
			"metric_type": "delivery_health",
		}

	return {
		"intent": "unknown",
		"metric_type": "unknown",
	}
