from src.services.metrics_service import load_metrics_data, get_metric_summary
from src.rag.context_builder import build_risk_evidence


def run_risk_analysis() -> dict:
	df = load_metrics_data()
	summary = get_metric_summary(df)

	evidence = build_risk_evidence(summary["risks"])

	return {
    	"tool_name": "risk_tool",
    	"tool_description": "Identifies domains with elevated delivery risk.",
    	"evidence": evidence,
    	"raw_data": summary["risks"].to_dict(orient="records"),
	}