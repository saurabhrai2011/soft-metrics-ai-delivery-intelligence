"""Run the golden eval set against the delivery-intelligence agent.

Usage:
    python scripts/run_evals.py
    python scripts/run_evals.py --only G1,G4
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from src.agents.orchestrator import DeliveryIntelligenceAgent
from src.observability.evaluation_logger import (
    append_result,
    open_run,
    write_summary,
)

GOLDEN_PATH = PROJECT_ROOT / "evals" / "golden.jsonl"


def load_golden(only: set[str] | None) -> list[dict]:
    rows = [json.loads(line) for line in GOLDEN_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    if only:
        rows = [r for r in rows if r["id"] in only]
    return rows


def tools_called(trace: list[dict]) -> list[str]:
    called = []
    for step in trace:
        for block in step.get("content", []):
            if block.get("type") == "tool_use":
                called.append(block.get("name"))
    return called


def check_tool(expected: str | None, called: list[str]) -> dict:
    if expected is None:
        return {"expected": None, "actual": called, "pass": True, "note": "no tool constraint"}
    return {"expected": expected, "actual": called, "pass": expected in called}


def check_contains(needles: list[str], haystack: str) -> dict:
    hay = haystack.lower()
    missing = [n for n in needles if n.lower() not in hay]
    return {"missing": missing, "pass": len(missing) == 0}


def check_must_not_name(forbidden: list[str], haystack: str) -> dict:
    hay = haystack.lower()
    violations = [f for f in forbidden if f.lower() in hay]
    return {"violations": violations, "pass": len(violations) == 0}


def check_citations(required: bool, citation_check: dict) -> dict:
    cited = citation_check.get("cited_ids", [])
    invalid = citation_check.get("invalid_ids", [])
    if not required:
        return {"required": False, "cited_ids": cited, "invalid_ids": invalid, "pass": True}
    return {
        "required": True,
        "cited_ids": cited,
        "invalid_ids": invalid,
        "pass": len(cited) > 0 and len(invalid) == 0,
    }


def grade(row: dict, agent_result: dict, latency_ms: int) -> dict:
    answer = agent_result["answer"]
    called = tools_called(agent_result["trace"])

    checks = {
        "tool_match": check_tool(row.get("expected_tool"), called),
        "entity_recall": check_contains(row.get("expected_entities", []), answer),
        "phrase_recall": check_contains(row.get("expected_answer_contains", []), answer),
        "citation_valid": check_citations(row.get("must_cite_evidence", False), agent_result["citation_check"]),
        "refusal_guard": check_must_not_name(row.get("must_not_name", []), answer),
    }
    return {
        "id": row["id"],
        "category": row["category"],
        "question": row["question"],
        "answer": answer,
        "tools_called": called,
        "checks": checks,
        "overall_pass": all(c["pass"] for c in checks.values()),
        "latency_ms": latency_ms,
        "citation_check": agent_result["citation_check"],
    }


def print_row(r: dict) -> None:
    status = "PASS" if r["overall_pass"] else "FAIL"
    failed = [name for name, c in r["checks"].items() if not c["pass"]]
    detail = f"  ({', '.join(failed)})" if failed else ""
    print(f"  {r['id']:<4} {r['category']:<22} {status}{detail}")
    if not r["overall_pass"]:
        preview = " ".join(r["answer"].split())[:200]
        print(f"        answer: {preview}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="Comma-separated question IDs to run (e.g. G1,G4)")
    args = parser.parse_args()

    only = set(args.only.split(",")) if args.only else None
    rows = load_golden(only)
    if not rows:
        print("No golden questions to run.")
        return 1

    run_path = open_run()
    print(f"Run id: {run_path.stem}  ({len(rows)} questions)\n")

    agent = DeliveryIntelligenceAgent()
    results: list[dict] = []

    for row in rows:
        t0 = time.time()
        try:
            agent_result = agent.run(row["question"])
        except Exception as e:
            agent_result = {
                "answer": f"ERROR: {e}",
                "evidence": [],
                "raw_data": [],
                "citation_check": {"valid": False, "cited_ids": [], "invalid_ids": []},
                "trace": [],
            }
        latency_ms = int((time.time() - t0) * 1000)
        graded = grade(row, agent_result, latency_ms)
        results.append(graded)
        append_result(run_path, graded)
        print_row(graded)

    summary_path = write_summary(run_path, results)
    passed = sum(1 for r in results if r["overall_pass"])
    print(f"\nOverall: {passed}/{len(results)}  ({round(100 * passed / len(results))}%)")
    print(f"Scorecard:  {run_path.relative_to(PROJECT_ROOT)}")
    print(f"Summary:    {summary_path.relative_to(PROJECT_ROOT)}")
    return 0 if passed == len(results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
