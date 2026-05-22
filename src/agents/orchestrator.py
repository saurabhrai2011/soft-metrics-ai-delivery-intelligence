"""Delivery-intelligence agent: Claude picks the tool, executes via run_agent loop."""

from __future__ import annotations

from src.agents.tools import (
    run_metrics_explainer,
    run_narrative_generator,
    run_rca_analysis,
    run_risk_analysis,
)
from src.agents.tools.query_metrics import query_metrics
from src.llm.anthropic_provider import run_agent
from src.rag.citation_validator import validate_citations


SYSTEM_PROMPT = """You are an AI Delivery Intelligence Assistant for software engineering leaders.

You have tools that return evidence about initiatives, capabilities, and epics.
Pick the tool that best fits the user's question. You may call multiple tools.

Grounding rules:
- Answer using ONLY the evidence returned by tools.
- Every factual claim must cite an evidence ID in square brackets, e.g. [E1].
- Use the exact IDs you see in tool results — do not renumber.
- Do not invent metrics, owners, teams, or causes.
- If evidence is insufficient, say so explicitly.

Answer format:
1. Direct Answer
2. Supporting Evidence (with [E#] citations)
3. Recommended Action (only if supported by evidence)
"""


TOOLS = [
    {
        "name": "query_metrics",
        "description": (
            "Run a read-only SQL SELECT against the delivery dataset. "
            "Use this for any counting, listing, filtering, trend, or join question. "
            "Tables:\n"
            "  initiatives(initiative_id, initiative_name, owner, start_date, "
            "target_end_date, budget_aud_m, strategic_priority, status)\n"
            "  capabilities(capability_id, capability_name, initiative_id, owner, "
            "start_date, planned_end_date, actual_end_date, status, completion_pct)\n"
            "  epics(epic_id, epic_name, capability_id, team, owner, priority, "
            "story_points, start_date, planned_end_date, actual_end_date, "
            "cycle_time_days, status, days_in_current_status, defect_count)\n"
            "Join capabilities to initiatives on initiative_id; epics to capabilities "
            "on capability_id. DuckDB SQL. Always include LIMIT."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {"type": "string", "description": "A DuckDB SELECT query."}
            },
            "required": ["sql"],
        },
    },
    {
        "name": "run_rca_analysis",
        "description": (
            "Root-cause analysis over current bottlenecks. Use when the user asks "
            "WHY something is slow, what is causing delays, or what is driving "
            "defects. Returns ranked bottleneck evidence."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "run_risk_analysis",
        "description": (
            "Identify domains/initiatives at elevated delivery risk. Use when the "
            "user asks what is at risk, behind schedule, slipping, or likely to "
            "miss a target date."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "run_narrative_generator",
        "description": (
            "Generate an executive-style delivery narrative from current health "
            "metrics. Use when the user asks for a leadership summary, status "
            "update, or executive narrative."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "run_metrics_explainer",
        "description": (
            "Explain delivery health metrics by domain. Use for general questions "
            "about how a domain is performing when no other tool fits better."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
]


class DeliveryIntelligenceAgent:
    """Claude-driven agent: tool selection happens inside the model, not here."""

    def run(self, question: str) -> dict:
        collected_evidence: list[dict] = []
        collected_raw: list[dict] = []

        def _reid_and_format(local_evidence: list[dict]) -> str:
            start = len(collected_evidence)
            lines = []
            for offset, item in enumerate(local_evidence):
                new_id = f"E{start + offset + 1}"
                reided = {**item, "id": new_id}
                collected_evidence.append(reided)
                lines.append(f"[{new_id}] {reided['text']}")
            return "\n".join(lines) if lines else "No evidence returned."

        def _wrap(fn):
            def handler(_input):
                result = fn()
                collected_raw.extend(result.get("raw_data", []))
                return _reid_and_format(result.get("evidence", []))
            return handler

        def _query_metrics_handler(input_dict):
            result = query_metrics(input_dict["sql"])
            if result.get("error") and not result["evidence"]:
                return f"ERROR: {result['error']}"
            collected_raw.extend(result.get("raw_data", []))
            formatted = _reid_and_format(result.get("evidence", []))
            return formatted + (f"\n[{result['error']}]" if result.get("error") else "")

        tool_handlers = {
            "query_metrics": _query_metrics_handler,
            "run_rca_analysis": _wrap(run_rca_analysis),
            "run_risk_analysis": _wrap(run_risk_analysis),
            "run_narrative_generator": _wrap(run_narrative_generator),
            "run_metrics_explainer": _wrap(run_metrics_explainer),
        }

        result = run_agent(
            user_question=question,
            tools=TOOLS,
            tool_handlers=tool_handlers,
            system=SYSTEM_PROMPT,
        )

        answer = result["answer"]
        citation_check = validate_citations(answer, collected_evidence)

        return {
            "question": question,
            "answer": answer,
            "evidence": collected_evidence,
            "raw_data": collected_raw,
            "citation_check": citation_check,
            "trace": result["trace"],
        }
