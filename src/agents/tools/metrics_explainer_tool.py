from src.services.metrics_service import load_metrics_data, get_metric_summary
from src.rag.context_builder import build_health_evidence


def run_metrics_explainer() -> dict:
	df = load_metrics_data()
	summary = get_metric_summary(df)

	evidence = build_health_evidence(summary["health"])

	return {
    	"tool_name": "metrics_explainer_tool",
    	"tool_description": "Explains delivery health metrics by domain.",
    	"evidence": evidence,
    	"raw_data": summary["health"].to_dict(orient="records"),
	}