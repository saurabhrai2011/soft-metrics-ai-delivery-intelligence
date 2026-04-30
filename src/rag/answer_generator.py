def generate_answer(question: str, plan: dict, evidence: list[dict]) -> str:
	if plan["metric_type"] == "bottleneck":
		if not evidence:
			return "I could not find enough evidence to identify bottlenecks."

		top = evidence[0]
		return (
			f"The main bottleneck appears to be: {top['text']} [{top['id']}]\n\n"
			"Recommended action: Review work items waiting in this status, check dependency delays, "
			"and confirm whether teams are blocked by approvals, environment readiness, or handover gaps."
		)

	if plan["metric_type"] == "risk":
		high_risk = [e for e in evidence if "risk level 'High'" in e["text"]]

		if high_risk:
			risk_lines = "\n".join([f"- {e['text']} [{e['id']}]" for e in high_risk])
			return (
				"The following domains show high delivery risk:\n\n"
				f"{risk_lines}\n\n"
				"Recommended action: Prioritise these domains for delivery review, dependency resolution, "
				"and focused intervention."
			)

		return (
			"No high-risk domains were found in the available dataset. "
			"Review medium-risk areas for early intervention."
		)

	if plan["metric_type"] == "commitment":
		lines = "\n".join([f"- {e['text']} [{e['id']}]" for e in evidence])
		return (
			"Commitment reliability summary:\n\n"
			f"{lines}\n\n"
			"Recommended action: Focus on domains below target reliability and inspect where planned work "
			"is not converting into delivered outcomes."
		)

	if plan["metric_type"] == "operational_health":
		lines = "\n".join([f"- {e['text']} [{e['id']}]" for e in evidence])
		return (
			"Operational health summary based on available metrics:\n\n"
			f"{lines}\n\n"
			"Recommended action: Review MTTR and incident trends for domains with weaker recovery performance."
		)

	if plan["metric_type"] == "delivery_health":
		lines = "\n".join([f"- {e['text']} [{e['id']}]" for e in evidence])
		return (
			"Executive delivery health summary:\n\n"
			f"{lines}\n\n"
			"Overall, the focus should be on domains with higher wait time, lower commitment reliability, "
			"and increasing operational load."
		)

	return (
		"I could not confidently answer this question from the available metrics. "
		"Please ask about delivery health, bottlenecks, risk, commitment, MTTR, or incidents."
	)
