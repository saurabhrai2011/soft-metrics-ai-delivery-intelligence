from src.services.metrics_service import (
	load_metrics_data,
	get_metric_summary,
)
from src.rag.query_planner import classify_question
from src.rag.context_builder import (
	build_bottleneck_evidence,
	build_risk_evidence,
	build_health_evidence,
)
from src.rag.answer_generator import generate_answer
from src.rag.citation_validator import validate_citations


def answer_question(question: str) -> dict:
	df = load_metrics_data()
	summary = get_metric_summary(df)

	plan = classify_question(question)

	if plan["metric_type"] == "bottleneck":
		evidence = build_bottleneck_evidence(summary["bottlenecks"])

	elif plan["metric_type"] == "risk":
		evidence = build_risk_evidence(summary["risks"])

	elif plan["metric_type"] in [
		"commitment",
		"operational_health",
		"delivery_health",
	]:
		evidence = build_health_evidence(summary["health"])

	else:
		evidence = []

	answer = generate_answer(question, plan, evidence)
	citation_check = validate_citations(answer, evidence)

	return {
		"question": question,
		"plan": plan,
		"answer": answer,
		"evidence": evidence,
		"citation_check": citation_check,
	}
