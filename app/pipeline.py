import os
import traceback
from datetime import datetime, timedelta

from app.config import DB_PATH, INPUT_CSV_PATH, OUTPUT_DIR, REPORT_LAST_N_DAYS

from app.db import get_conn
from app.import_csv import import_csv_to_raw

import app.transform as transform
from app.transform import rebuild_facts

from app.validation import validate_input_dataframe
from app.data_quality import analyze_raw_dataframe, build_quality_notes

from app.queries import (
    get_date_range,
    kpi_summary,
    top_categories,
    daily_trend,
    period_comparison,
)

from app.charts import ensure_dir, plot_trend, plot_top_categories
from app.decision import simple_decision
from app.llm_insights import generate_insights
from app.pdf_report import build_pdf
from app.run_log import init_run_log, save_run

def select_reporting_period(max_date: str, last_n_days: int) -> tuple[str, str]:
    date_format = "%Y-%m-%d"

    end = datetime.strptime(max_date, date_format)
    start = end - timedelta(days=last_n_days - 1)

    return start.strftime(date_format), end.strftime(date_format)


def generate_report(
    input_csv_path: str | None = None,
    report_last_n_days: int | None = None,
) -> str:
    """
    Main pipeline function used by both:
    - CLI mode: python main.py
    - Desktop GUI: desktop_app.py / AutoReport.exe

    Returns path to generated PDF.
    """

    selected_csv = input_csv_path or INPUT_CSV_PATH
    selected_last_n_days = report_last_n_days or REPORT_LAST_N_DAYS

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    charts_dir = os.path.join(OUTPUT_DIR, "charts")
    ensure_dir(charts_dir)

    conn = get_conn(DB_PATH)
    init_run_log(conn)

    output_pdf = os.path.join(OUTPUT_DIR, "report.pdf")

    params = {
        "input_csv": selected_csv,
        "output_dir": OUTPUT_DIR,
        "report_last_n_days": selected_last_n_days,
    }

    try:
        # -------------------------
        # 1. IMPORT CSV -> RAW TABLE
        # -------------------------
        raw_df = import_csv_to_raw(selected_csv)

        # -------------------------
        # 2. INPUT VALIDATION
        # -------------------------
        validate_input_dataframe(
            raw_df,
            date_col=transform.DATE_COL,
            value_col=transform.VALUE_COL,
            category_col=transform.CATEGORY_COL,
        )

        # -------------------------
        # 3. DATA QUALITY
        # -------------------------
        data_quality = analyze_raw_dataframe(
            raw_df,
            date_col=transform.DATE_COL,
            value_col=transform.VALUE_COL,
            category_col=transform.CATEGORY_COL,
        )

        data_quality_notes = build_quality_notes(data_quality)

        # -------------------------
        # 4. TRANSFORM RAW -> FACTS
        # -------------------------
        rebuild_facts()

        # -------------------------
        # 5. DATE RANGE / REPORTING PERIOD
        # -------------------------
        date_range = get_date_range(conn)
        min_date = date_range["min_date"]
        max_date = date_range["max_date"]

        if min_date is None or max_date is None:
            raise ValueError("No valid date range found in facts table.")

        start_date, end_date = select_reporting_period(
            max_date=max_date,
            last_n_days=selected_last_n_days,
        )

        # -------------------------
        # 6. SQL QUERIES / KPI ENGINE
        # -------------------------
        kpis = kpi_summary(conn, start_date, end_date)
        top = top_categories(conn, start_date, end_date, limit=5)
        daily = daily_trend(conn, start_date, end_date)
        comparison = period_comparison(conn, start_date, end_date)

        if kpis["rows_cnt"] == 0:
            raise ValueError(
                f"No rows found for selected reporting period: {start_date} -> {end_date}"
            )

        # -------------------------
        # 7. CHARTS
        # -------------------------
        trend_path = plot_trend(
            daily,
            os.path.join(charts_dir, "trend.png"),
        )

        top_categories_path = plot_top_categories(
            top,
            os.path.join(charts_dir, "top_categories.png"),
        )

        chart_paths = {
            "trend": trend_path,
            "top_categories": top_categories_path,
        }

        # -------------------------
        # 8. DECISION LAYER
        # -------------------------
        decision = simple_decision(comparison)

        # -------------------------
        # 9. LLM / FALLBACK INSIGHTS
        # -------------------------
        report_payload = {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
            },
            "source_data_range": {
                "min_date": min_date,
                "max_date": max_date,
            },
            "kpis": kpis,
            "comparison": comparison,
            "top_categories": top,
            "daily_points": daily[-7:],
            "data_quality": data_quality,
            "decision": decision,
        }

        insights = generate_insights(report_payload)

        # -------------------------
        # 10. PDF REPORT
        # -------------------------
        build_pdf(
            out_pdf=output_pdf,
            meta={"title": "Auto Report"},
            kpis=kpis,
            comparison=comparison,
            top_categories=top,
            insights=insights,
            chart_paths=chart_paths,
            decision=decision,
            data_quality_notes=data_quality_notes,
        )

        # -------------------------
        # 11. RUN LOG
        # -------------------------
        params.update(
            {
                "source_min_date": min_date,
                "source_max_date": max_date,
                "start_date": start_date,
                "end_date": end_date,
                "date_col": transform.DATE_COL,
                "value_col": transform.VALUE_COL,
                "category_col": transform.CATEGORY_COL,
            }
        )

        save_run(
            conn=conn,
            params=params,
            kpis=kpis,
            comparison=comparison,
            insights=insights,
            output_pdf=output_pdf,
            error_text=None,
        )

        print(f"✅ REPORT GENERATED: {output_pdf}")
        print(f"📅 Source data range: {min_date} -> {max_date}")
        print(f"📊 Reporting period: {start_date} -> {end_date}")
        print(f"🧾 Rows analyzed: {kpis['rows_cnt']}")
        print(f"⚖️ Decision: {decision}")

        return output_pdf

    except Exception as error:
        error_text = f"{type(error).__name__}: {error}"

        print(f"❌ ERROR: {error_text}")
        print(traceback.format_exc())

        try:
            save_run(
                conn=conn,
                params=params,
                kpis={},
                comparison={},
                insights={},
                output_pdf=output_pdf,
                error_text=error_text,
            )
        except Exception as log_error:
            print(f"⚠️ Could not save error log: {log_error}")

        raise

    finally:
        conn.close()


def main():
    generate_report()


if __name__ == "__main__":
    main()