from src.services.metrics_service import load_metrics_data, get_metric_summary
from src.rag.context_builder import build_bottleneck_evidence


def run_rca_analysis() -> dict:
	df = load_metrics_data()
	summary = get_metric_summary(df)

	evidence = build_bottleneck_evidence(summary["bottlenecks"])

	return {
		"tool_name": "rca_tool",
		"tool_description": "Performs lightweight root cause analysis using bottleneck evidence.",
		"evidence": evidence,
		"raw_data": summary["bottlenecks"].to_dict(orient="records"),
	}
