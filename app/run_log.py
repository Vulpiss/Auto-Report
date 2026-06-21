import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional, List


def init_run_log(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS report_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        params_json TEXT NOT NULL,
        kpis_json TEXT NOT NULL,
        comparison_json TEXT NOT NULL,
        insights_json TEXT NOT NULL,
        output_pdf TEXT NOT NULL,
        error_text TEXT
    )
    """)

    conn.commit()


def save_run(
    conn: sqlite3.Connection,
    params: Dict[str, Any],
    kpis: Dict[str, Any],
    comparison: Dict[str, Any],
    insights: Dict[str, Any],
    output_pdf: str,
    error_text: Optional[str] = None
) -> None:
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO report_runs (
        created_at,
        params_json,
        kpis_json,
        comparison_json,
        insights_json,
        output_pdf,
        error_text
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        json.dumps(params, ensure_ascii=False),
        json.dumps(kpis, ensure_ascii=False),
        json.dumps(comparison, ensure_ascii=False),
        json.dumps(insights, ensure_ascii=False),
        output_pdf,
        error_text
    ))

    conn.commit()


def get_recent_runs(
    conn: sqlite3.Connection,
    limit: int = 10
) -> List[Dict[str, Any]]:
    cur = conn.cursor()

    cur.execute("""
    SELECT
        id,
        created_at,
        params_json,
        kpis_json,
        comparison_json,
        insights_json,
        output_pdf,
        error_text
    FROM report_runs
    ORDER BY id DESC
    LIMIT ?
    """, (limit,))

    rows = cur.fetchall()

    result = []

    for row in rows:
        result.append({
            "id": row["id"],
            "created_at": row["created_at"],
            "params": json.loads(row["params_json"] or "{}"),
            "kpis": json.loads(row["kpis_json"] or "{}"),
            "comparison": json.loads(row["comparison_json"] or "{}"),
            "insights": json.loads(row["insights_json"] or "{}"),
            "output_pdf": row["output_pdf"],
            "error_text": row["error_text"],
        })

    return result