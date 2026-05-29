"""query_metrics tool: run SQL over the synthetic delivery dataset via DuckDB."""

from __future__ import annotations
from pathlib import Path
import duckdb

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "synthetic"
MAX_ROWS = 50

_con = duckdb.connect(":memory:")
_con.execute(f"CREATE VIEW initiatives  AS SELECT * FROM read_csv_auto('{(DATA_DIR / 'Initiative_Extract.csv').as_posix()}')")
_con.execute(f"CREATE VIEW capabilities AS SELECT * FROM read_csv_auto('{(DATA_DIR / 'Capability_Extract.csv').as_posix()}')")
_con.execute(f"CREATE VIEW epics        AS SELECT * FROM read_csv_auto('{(DATA_DIR / 'Epic_Extract.csv').as_posix()}')")


def query_metrics(sql: str) -> dict:
    """
    Run a read-only SQL query against the delivery dataset.

    Returns: {"evidence": [...], "raw_data": [...], "error": str | None}
    Each result row becomes one evidence item the agent can cite.
    """
    lowered = sql.strip().lower()
    forbidden = ("insert", "update", "delete", "drop", "create", "alter", "attach")
    if any(lowered.startswith(kw) or f" {kw} " in lowered for kw in forbidden):
        return {"evidence": [], "raw_data": [], "error": "only SELECT queries are allowed."}

    try:
        df = _con.execute(sql).fetchdf()
    except Exception as e:
        return {"evidence": [], "raw_data": [], "error": f"{type(e).__name__}: {e}"}

    if df.empty:
        return {"evidence": [], "raw_data": [], "error": None}

    truncated = len(df) > MAX_ROWS
    df = df.head(MAX_ROWS)
    rows = df.to_dict(orient="records")

    evidence = [
        {
            "id": f"E{i + 1}",
            "type": "sql_row",
            "text": ", ".join(f"{k}={v}" for k, v in row.items()),
        }
        for i, row in enumerate(rows)
    ]

    return {
        "evidence": evidence,
        "raw_data": rows,
        "error": f"truncated — showing first {MAX_ROWS} rows" if truncated else None,
    }
