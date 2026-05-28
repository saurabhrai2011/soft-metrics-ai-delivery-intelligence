"""Append per-question eval results and write aggregate scorecards."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCORECARD_DIR = PROJECT_ROOT / "evals" / "scorecards"


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def open_run(run_id: str | None = None) -> Path:
    SCORECARD_DIR.mkdir(parents=True, exist_ok=True)
    rid = run_id or _run_id()
    path = SCORECARD_DIR / f"{rid}.jsonl"
    path.touch()
    return path


def append_result(path: Path, result: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, default=str) + "\n")


def write_summary(path: Path, results: list[dict]) -> Path:
    total = len(results)
    passed = sum(1 for r in results if r["overall_pass"])
    citation_valid = sum(1 for r in results if r["checks"]["citation_valid"]["pass"])
    avg_latency = round(sum(r["latency_ms"] for r in results) / total, 1) if total else 0

    summary = {
        "run_id": path.stem,
        "total": total,
        "passed": passed,
        "pass_rate": round(passed / total, 3) if total else 0,
        "citation_validity": f"{citation_valid}/{total}",
        "avg_latency_ms": avg_latency,
        "per_question": [
            {
                "id": r["id"],
                "category": r["category"],
                "pass": r["overall_pass"],
                "failed_checks": [
                    name for name, c in r["checks"].items() if not c["pass"]
                ],
            }
            for r in results
        ],
    }
    summary_path = path.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary_path
