import os
from dotenv import load_dotenv

from src.agents.tools import (
	run_metrics_explainer,
	run_narrative_generator,
	run_rca_analysis,
	run_risk_analysis,
	run_sql_query,
)
from src.llm.provider_factory import get_llm_provider
from src.llm.prompts import build_grounded_answer_prompt
from src.rag.citation_validator import validate_citations

load_dotenv()


class DeliveryIntelligenceAgent:
	"""
	Agentic orchestration layer.

	Responsibilities:
	1. Classify user intent.
	2. Select the right existing tool.
	3. Execute tool and retrieve evidence.
	4. Generate grounded answer using offline or live LLM provider.
	5. Validate citations.
	6. Return answer, evidence, and trace.
	"""

	def __init__(self):
		self.llm = get_llm_provider()

		self.tool_registry = {
			"metrics_explainer": run_metrics_explainer,
			"narrative": run_narrative_generator,
			"rca": run_rca_analysis,
			"risk": run_risk_analysis,
			"sql_query": run_sql_query,
		}

	def classify_intent(self, question: str) -> dict:
		q = question.lower()

		if "root cause" in q or "why" in q or "cause" in q:
			return {
				"intent": "root_cause_analysis",
				"tool_key": "rca",
				"reason": "Question asks why something is happening or asks for root cause.",
			}

		if "risk" in q or "behind" in q or "delay" in q or "likely to miss" in q:
			return {
				"intent": "risk_analysis",
				"tool_key": "risk",
				"reason": "Question asks about delivery risk or delayed areas.",
			}

		if "executive" in q or "summary" in q or "narrative" in q:
			return {
				"intent": "executive_narrative",
				"tool_key": "narrative",
				"reason": "Question asks for a leadership summary or narrative.",
			}

		if "sql" in q or "query" in q or "table" in q:
			return {
				"intent": "structured_query",
				"tool_key": "sql_query",
				"reason": "Question asks for structured query or tabular metric output.",
			}

		return {
			"intent": "metrics_explanation",
			"tool_key": "metrics_explainer",
			"reason": "Defaulting to general metrics explanation.",
		}

	def run_selected_tool(self, tool_key: str) -> dict:
		if tool_key == "sql_query":
			return self.tool_registry[tool_key](query_type="delivery_health")

		return self.tool_registry[tool_key]()

	def run(self, question: str) -> dict:
		plan = self.classify_intent(question)
		tool_key = plan["tool_key"]

		tool_result = self.run_selected_tool(tool_key)
		evidence = tool_result.get("evidence", [])

		agent_trace = {
			"question": question,
			"intent": plan["intent"],
			"selected_tool": tool_result.get("tool_name"),
			"tool_reason": plan["reason"],
			"llm_provider": os.getenv("LLM_PROVIDER", "offline"),
			"use_llm": os.getenv("USE_LLM", "false"),
		}

		prompt = build_grounded_answer_prompt(
			question=question,
			evidence=evidence,
			agent_trace=agent_trace,
		)

		answer = self.llm.complete(prompt)

		citation_check = validate_citations(answer, evidence)

		return {
			"question": question,
			"plan": plan,
			"agent_trace": agent_trace,
			"answer": answer,
			"evidence": evidence,
			"citation_check": citation_check,
			"raw_data": tool_result.get("raw_data", []),
		}
