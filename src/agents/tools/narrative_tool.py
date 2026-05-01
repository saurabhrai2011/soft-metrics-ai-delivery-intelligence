from src.services.metrics_service import load_metrics_data, get_metric_summary
from src.rag.context_builder import build_health_evidence


def run_narrative_generator() -> dict:
	df = load_metrics_data()
	summary = get_metric_summary(df)

	evidence = build_health_evidence(summary["health"])

	return {
    	"tool_name": "narrative_tool",
    	"tool_description": "Generates executive delivery narrative from metrics evidence.",
    	"evidence": evidence,
    	"raw_data": summary["health"].to_dict(orient="records"),
	}