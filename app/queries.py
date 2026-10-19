from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import math

DATE_FORMAT = "%Y-%m-%d"


def _period(start, end):
    a, b = datetime.strptime(start, DATE_FORMAT), datetime.strptime(end, DATE_FORMAT)
    if a.strftime(DATE_FORMAT) != start or b.strftime(DATE_FORMAT) != end:
        raise ValueError("Daty okresu muszą mieć format RRRR-MM-DD.")
    if a > b:
        raise ValueError("Początek okresu musi poprzedzać jego koniec.")
    return a, b


def get_date_range(conn):
    row = conn.execute("SELECT MIN(event_date), MAX(event_date) FROM facts").fetchone()
    return {"min_date": row[0], "max_date": row[1]}


def kpi_summary(conn, start_date, end_date):
    _period(start_date, end_date)
    count, total = conn.execute("SELECT COUNT(*), COALESCE(SUM(value_minor), 0) FROM facts WHERE event_date BETWEEN ? AND ?", (start_date, end_date)).fetchone()
    average = (Decimal(total) / (100 * count)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if count else Decimal(0)
    return {"rows_cnt": count, "total_minor": total, "total_value": Decimal(total) / 100,
            "avg_value": average, "start_date": start_date, "end_date": end_date}


def top_categories(conn, start_date, end_date, limit=5):
    _period(start_date, end_date)
    rows = conn.execute("SELECT category, SUM(value_minor) FROM facts WHERE event_date BETWEEN ? AND ? GROUP BY category ORDER BY SUM(value_minor) DESC, category ASC LIMIT ?", (start_date, end_date, limit))
    return [{"category": r[0], "total_minor": r[1], "total_value": Decimal(r[1]) / 100} for r in rows]


def daily_trend(conn, start_date, end_date):
    _period(start_date, end_date)
    rows = conn.execute("SELECT event_date, SUM(value_minor) FROM facts WHERE event_date BETWEEN ? AND ? GROUP BY event_date ORDER BY event_date", (start_date, end_date))
    return [{"event_date": r[0], "total_minor": r[1], "total_value": Decimal(r[1]) / 100} for r in rows]


def compute_previous_period(start_date, end_date):
    start, end = _period(start_date, end_date)
    previous_end = start - timedelta(days=1)
    previous_start = previous_end - (end - start)
    return previous_start.strftime(DATE_FORMAT), previous_end.strftime(DATE_FORMAT)


def calculate_pct_change(current, previous):
    # Percentages relative to zero or a negative net base are not meaningful here.
    if not math.isfinite(current) or not math.isfinite(previous) or previous <= 0:
        return None
    return float((current - previous) / previous * 100)


def period_comparison(conn, start_date, end_date, coverage_start=None, coverage_end=None):
    previous_start, previous_end = compute_previous_period(start_date, end_date)
    current = kpi_summary(conn, start_date, end_date)
    previous = kpi_summary(conn, previous_start, previous_end)
    if bool(coverage_start) != bool(coverage_end):
        raise ValueError("Podaj obie granice kompletnego eksportu.")
    if coverage_start:
        _period(coverage_start, coverage_end)
    verified = bool(coverage_start and coverage_start <= previous_start and coverage_end >= end_date)
    available = verified and previous["rows_cnt"] > 0
    if not verified:
        reason = "Nie potwierdzono pełnego eksportu dla obu okresów."
    elif not previous["rows_cnt"]:
        reason = "Poprzedni okres nie zawiera pozycji."
    else:
        reason = "Zakres eksportu potwierdzony przez użytkownika; baza 0 lub ujemna daje N/A."
    changes = {key: calculate_pct_change(current[key], previous[key]) if available else None
               for key in ("total_value", "avg_value", "rows_cnt")}
    if available and current["rows_cnt"]:
        changes["avg_value"] = calculate_pct_change(current["total_minor"] / current["rows_cnt"], previous["total_minor"] / previous["rows_cnt"])
    return {"current": current, "previous": previous, "baseline_available": available,
            "coverage_verified": verified, "reason": reason, "change_pct": changes}
