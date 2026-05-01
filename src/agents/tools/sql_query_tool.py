from src.services.metrics_service import load_metrics_data, get_metric_summary
from src.rag.context_builder import build_health_evidence


def run_sql_query(query_type: str = "delivery_health") -> dict:
	df = load_metrics_data()
	summary = get_metric_summary(df)

	evidence = build_health_evidence(summary["health"])

	return {
		"tool_name": "sql_query_tool",
		"tool_description": f"Returns structured tabular metric data for query type: {query_type}.",
		"evidence": evidence,
		"raw_data": summary["health"].to_dict(orient="records"),
	}
