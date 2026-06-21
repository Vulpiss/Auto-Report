from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

from app.db import fetch_all

DATE_FORMAT = "%Y-%m-%d"


def get_date_range(conn) -> Dict[str, Any]:
    row = fetch_all(
        conn,
        """
        SELECT 
            MIN(event_date) AS min_d, 
            MAX(event_date) AS max_d 
        FROM facts;
        """
    )[0]

    return {
        "min_date": row["min_d"],
        "max_date": row["max_d"]
    }


def kpi_summary(conn, start_date: str, end_date: str) -> Dict[str, Any]:
    row = fetch_all(
        conn,
        """
        SELECT
            COUNT(*) AS rows_cnt,
            SUM(value) AS total_value,
            AVG(value) AS avg_value
        FROM facts
        WHERE event_date BETWEEN ? AND ?;
        """,
        [start_date, end_date]
    )[0]

    return {
        "rows_cnt": int(row["rows_cnt"] or 0),
        "total_value": float(row["total_value"] or 0.0),
        "avg_value": float(row["avg_value"] or 0.0),
        "start_date": start_date,
        "end_date": end_date
    }


def top_categories(
        conn,
        start_date: str,
        end_date: str,
        limit: int = 5
) -> List[Dict[str, Any]]:
    rows = fetch_all(
        conn,
        """
        SELECT 
            category, 
            SUM(value) AS total_value
        FROM facts
        WHERE event_date BETWEEN ? AND ?
        GROUP BY category
        ORDER BY total_value DESC
        LIMIT ?;
        """,
        [start_date, end_date, limit]
    )

    return [
        {
            "category": row["category"],
            "total_value": float(row["total_value"] or 0.0)
        }
        for row in rows
    ]


def daily_trend(conn, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    rows = fetch_all(
        conn,
        """
        SELECT 
            event_date, 
            SUM(value) AS total_value
        FROM facts
        WHERE event_date BETWEEN ? AND ?
        GROUP BY event_date
        ORDER BY event_date ASC;
        """,
        [start_date, end_date]
    )

    return [
        {
            "event_date": row["event_date"],
            "total_value": float(row["total_value"] or 0.0)
        }
        for row in rows
    ]


def compute_previous_period(start_date: str, end_date: str) -> Tuple[str, str]:
    """
    Liczy poprzedni okres o tej samej długości.

    Przykład:
    current: 2024-04-01 → 2024-04-30
    previous: 2024-03-02 → 2024-03-31

    Uwaga:
    BETWEEN w SQL jest inclusive, więc liczba dni to:
    (end - start).days + 1
    """
    start = datetime.strptime(start_date, DATE_FORMAT)
    end = datetime.strptime(end_date, DATE_FORMAT)

    period_days = (end - start).days + 1

    previous_end = start - timedelta(days=1)
    previous_start = previous_end - timedelta(days=period_days - 1)

    return (
        previous_start.strftime(DATE_FORMAT),
        previous_end.strftime(DATE_FORMAT)
    )


def calculate_pct_change(current: float, previous: float) -> float:
    """
    Liczy zmianę procentową.

    Jeśli previous = 0:
    - current = 0 → 0%
    - current > 0 → 100%

    Nie dajemy 999%, bo to wygląda jak fake.
    """
    if previous == 0:
        if current == 0:
            return 0.0
        return 100.0

    return ((current - previous) / previous) * 100.0


def period_comparison(conn, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Porównuje obecny okres z poprzednim okresem o tej samej długości.
    """

    previous_start, previous_end = compute_previous_period(start_date, end_date)

    current = kpi_summary(conn, start_date, end_date)
    previous = kpi_summary(conn, previous_start, previous_end)

    change_pct = {
        "total_value": calculate_pct_change(
            current["total_value"],
            previous["total_value"]
        ),
        "avg_value": calculate_pct_change(
            current["avg_value"],
            previous["avg_value"]
        ),
        "rows_cnt": calculate_pct_change(
            current["rows_cnt"],
            previous["rows_cnt"]
        )
    }

    return {
        "current": current,
        "previous": previous,
        "baseline_available": previous["rows_cnt"] > 0,
        "change_pct": change_pct
    }