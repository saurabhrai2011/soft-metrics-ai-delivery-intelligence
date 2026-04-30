def build_bottleneck_evidence(bottlenecks_df):
	evidence = []

	for _, row in bottlenecks_df.head(3).iterrows():
		evidence.append(
			{
				"id": f"E{len(evidence) + 1}",
				"type": "status_metric",
				"text": (
					f"Status '{row['status']}' has average wait time "
					f"of {row['avg_wait_time_days']} days across {row['count']} item(s)."
				),
			}
		)

	return evidence


def build_risk_evidence(risks_df):
	evidence = []

	for _, row in risks_df.iterrows():
		evidence.append(
			{
				"id": f"E{len(evidence) + 1}",
				"type": "domain_risk",
				"text": (
					f"Domain '{row['domain']}' has commitment reliability "
					f"of {row['commitment_reliability_pct']}%, average wait time "
					f"of {row['avg_wait_time_days']} days, and risk level '{row['risk_level']}'."
				),
			}
		)

	return evidence


def build_health_evidence(health_df):
	evidence = []

	for _, row in health_df.iterrows():
		evidence.append(
			{
				"id": f"E{len(evidence) + 1}",
				"type": "domain_health",
				"text": (
					f"Domain '{row['domain']}' has average lead time "
					f"{row['avg_lead_time_days']} days, average cycle time "
					f"{row['avg_cycle_time_days']} days, and commitment reliability "
					f"{row['commitment_reliability_pct']}%."
				),
			}
		)

	return evidence
