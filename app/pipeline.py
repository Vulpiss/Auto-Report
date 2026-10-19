"""Shared analysis and isolated, atomic PDF exports."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import threading
from uuid import uuid4
from app.config import INPUT_CSV_PATH, OUTPUT_DIR, REPORT_LAST_N_DAYS, VERSION
from app.validation import DataValidationError, currency_label
from app.analysis import analyze, select_reporting_period, ranked_categories
from app.decision import simple_decision
from app.llm_insights import generate_insights
from app.charts import plot_trend
from app.pdf_report import build_pdf

_REPORT_LOCK = threading.Lock()

def generate_report(input_csv_path=None, report_last_n_days=None, *, profile=None,
                    output_dir=None, start_date=None, end_date=None, categories=None,
                    coverage_start=None, coverage_end=None, title="Raport wartości pozycji"):
    if not _REPORT_LOCK.acquire(blocking=False):
        raise RuntimeError("Raport jest już generowany. Poczekaj na zakończenie.")
    try:
        result = analyze(input_csv_path if input_csv_path is not None else INPUT_CSV_PATH,
                         profile=profile, days=REPORT_LAST_N_DAYS if report_last_n_days is None else report_last_n_days,
                         start_date=start_date, end_date=end_date, categories=categories,
                         coverage_start=coverage_start, coverage_end=coverage_end)
        return _export(result, output_dir, title)
    finally:
        _REPORT_LOCK.release()

def export_analysis(result, *, output_dir=None, title="Raport wartości pozycji"):
    """Export the exact completed snapshot displayed in the dashboard."""
    if not _REPORT_LOCK.acquire(blocking=False):
        raise RuntimeError("Raport jest już generowany. Poczekaj na zakończenie.")
    try:
        return _export(result, output_dir, title)
    finally:
        _REPORT_LOCK.release()

def _export(result, output_dir, title):
    if not isinstance(title, str) or not title.strip() or len(title) > 160:
        raise ValueError("Tytuł raportu musi zawierać 1-160 znaków.")
    if result["status"] != "complete":
        raise DataValidationError("Wybrany okres nie zawiera pozycji.")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:12]
    root = Path(output_dir or OUTPUT_DIR).resolve()
    root.mkdir(parents=True, exist_ok=True)
    staging, final = root / (".pending-" + run_id), root / run_id
    staging.mkdir()
    summary = {key: result[key] for key in ("source_sha256", "source_range", "coverage_start", "coverage_end",
               "profile", "kpis", "comparison", "quality", "status", "selected_categories", "daily", "categories", "business", "dimensions", "selected_products", "selected_customers", "comparison_mode")}
    summary["comparison"] = dict(summary["comparison"], change_pct={k:float(v) if v is not None else None for k,v in summary["comparison"]["change_pct"].items()})
    summary.update(version=VERSION, template_version="4", run_id=run_id)
    try:
        plot_trend([r for r in result["daily"] if r["rows_cnt"]], str(staging / "trend.png"), currency=currency_label(result["profile"]))
        build_pdf(str(staging / "report.pdf"), dict(summary, title=title), result["kpis"], result["comparison"],
                  ranked_categories(result, 10), generate_insights(result),
                  {"trend": str(staging / "trend.png")}, simple_decision(result["comparison"]), result["notes"])
        (staging / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2,
                                           allow_nan=False, default=str), encoding="utf-8")
        os.replace(staging, final)
    except Exception as exc:
        try:
            (staging / "failure.json").write_text(json.dumps({"status": "failed", "error_type": type(exc).__name__}), encoding="utf-8")
        except OSError:
            # Full disks and inaccessible directories can also block diagnostics.
            # Preserve the original export error and always release the lock.
            exc.add_note("Nie udało się zapisać diagnostyki nieudanego eksportu.")
        raise
    return str(final / "report.pdf")

def main():
    print(generate_report())
