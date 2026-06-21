import os
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm


PAGE_MARGIN_X = 2 * cm
PAGE_MARGIN_TOP = 2 * cm
PAGE_MARGIN_BOTTOM = 1.5 * cm


def draw_footer(c: canvas.Canvas, page_num: int) -> None:
    c.setFont("Helvetica", 8)
    c.drawString(PAGE_MARGIN_X, 1 * cm, f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawRightString(A4[0] - PAGE_MARGIN_X, 1 * cm, f"Page {page_num}")


def new_page(c: canvas.Canvas, page_num: int) -> tuple[int, float]:
    draw_footer(c, page_num)
    c.showPage()
    page_num += 1
    y = A4[1] - PAGE_MARGIN_TOP
    return page_num, y


def draw_wrapped_text(c, text, x, y, max_width, line_height):
    words = str(text).split()
    line = ""
    lines = []

    for word in words:
        test_line = (line + " " + word).strip()
        if c.stringWidth(test_line) <= max_width:
            line = test_line
        else:
            if line:
                lines.append(line)
            line = word

    if line:
        lines.append(line)

    for line_text in lines:
        c.drawString(x, y, line_text)
        y -= line_height

    return y


def draw_section_title(c, title, y):
    c.setFont("Helvetica-Bold", 14)
    c.drawString(PAGE_MARGIN_X, y, title)
    y -= 0.5 * cm
    c.line(PAGE_MARGIN_X, y, A4[0] - PAGE_MARGIN_X, y)
    y -= 0.5 * cm
    return y


def draw_kpi_card(c, title, value, x, y, width=5 * cm, height=2 * cm):
    c.rect(x, y - height, width, height, stroke=1, fill=0)

    c.setFont("Helvetica-Bold", 9)
    c.drawString(x + 0.3 * cm, y - 0.6 * cm, title)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(x + 0.3 * cm, y - 1.4 * cm, value)


def draw_box(c, title, text, x, y, width=17 * cm, height=2.2 * cm):
    c.rect(x, y - height, width, height, stroke=1, fill=0)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(x + 0.3 * cm, y - 0.5 * cm, title)

    c.setFont("Helvetica", 10)
    draw_wrapped_text(
        c,
        text,
        x + 0.3 * cm,
        y - 1.0 * cm,
        max_width=width - 0.6 * cm,
        line_height=12,
    )

    return y - height - 0.5 * cm


def draw_bullets(c, title, items, x, y, page_num):
    width, height = A4

    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, title)
    y -= 0.45 * cm

    c.setFont("Helvetica", 10)

    for item in items:
        if y < PAGE_MARGIN_BOTTOM + 1.5 * cm:
            page_num, y = new_page(c, page_num)

        y = draw_wrapped_text(
            c,
            f"- {item}",
            x,
            y,
            max_width=17 * cm,
            line_height=12,
        )
        y -= 0.15 * cm

    y -= 0.25 * cm
    return y, page_num


def build_pdf(
    out_pdf: str,
    meta: Dict[str, Any],
    kpis: Dict[str, Any],
    comparison: Dict[str, Any],
    top_categories: List[Dict[str, Any]],
    insights: Dict[str, Any],
    chart_paths: Dict[str, str],
    decision: str,
    data_quality_notes: List[str],
):
    os.makedirs(os.path.dirname(out_pdf) or ".", exist_ok=True)

    c = canvas.Canvas(out_pdf, pagesize=A4)
    width, height = A4
    page_num = 1
    y = height - PAGE_MARGIN_TOP

    # -------------------------
    # HEADER
    # -------------------------
    c.setFont("Helvetica-Bold", 20)
    c.drawString(PAGE_MARGIN_X, y, f"Automated Data Report")
    y -= 0.8 * cm

    c.setFont("Helvetica", 11)
    c.drawString(PAGE_MARGIN_X, y, f"Report name: {meta.get('title', 'Dataset')}")
    y -= 0.45 * cm
    c.drawString(PAGE_MARGIN_X, y, f"Period: {kpis['start_date']} -> {kpis['end_date']}")
    y -= 0.8 * cm

    # -------------------------
    # KPI CARDS
    # -------------------------
    y = draw_section_title(c, "KPI Summary", y)

    draw_kpi_card(c, "Total value", f"{kpis['total_value']:,.2f}", PAGE_MARGIN_X, y)
    draw_kpi_card(c, "Average value", f"{kpis['avg_value']:,.2f}", PAGE_MARGIN_X + 6 * cm, y)
    draw_kpi_card(c, "Rows", f"{kpis['rows_cnt']}", PAGE_MARGIN_X + 12 * cm, y)

    y -= 2.7 * cm

    # -------------------------
    # DECISION
    # -------------------------
    y = draw_section_title(c, "Decision Layer", y)
    y = draw_box(c, "Decision", decision, PAGE_MARGIN_X, y)

    # -------------------------
    # PERIOD COMPARISON
    # -------------------------
    comparison_text = "Previous period has no data. Comparison unavailable."

    if comparison.get("baseline_available", False):
        ch = comparison["change_pct"]
        comparison_text = (
            f"Total change: {ch['total_value']:.1f}%. "
            f"Average change: {ch['avg_value']:.1f}%. "
            f"Rows change: {ch['rows_cnt']:.1f}%."
        )

    y = draw_box(c, "Period Comparison", comparison_text, PAGE_MARGIN_X, y)

    # -------------------------
    # CHARTS
    # -------------------------
    y = draw_section_title(c, "Charts", y)

    trend_chart = chart_paths.get("trend")
    top_categories_chart = chart_paths.get("top_categories")

    if trend_chart and os.path.exists(trend_chart):
        c.drawImage(
            trend_chart,
            PAGE_MARGIN_X,
            y - 7 * cm,
            width=17 * cm,
            height=6.5 * cm,
            preserveAspectRatio=True,
        )
        y -= 7.5 * cm
    else:
        c.setFont("Helvetica", 10)
        c.drawString(PAGE_MARGIN_X, y, "Trend chart unavailable.")
        y -= 0.6 * cm

    if top_categories_chart and os.path.exists(top_categories_chart):
        page_num, y = new_page(c, page_num)

        y = draw_section_title(c, "Top Categories", y)

        c.drawImage(
            top_categories_chart,
            PAGE_MARGIN_X,
            y - 8 * cm,
            width=17 * cm,
            height=7.5 * cm,
            preserveAspectRatio=True,
        )
        y -= 8.3 * cm
    else:
        c.setFont("Helvetica", 10)
        c.drawString(PAGE_MARGIN_X, y, "Top categories chart unavailable.")
        y -= 0.6 * cm

    # -------------------------
    # AI INSIGHTS
    # -------------------------
    page_num, y = new_page(c, page_num)

    y = draw_section_title(c, "AI Insights / Fallback Analysis", y)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(PAGE_MARGIN_X, y, "Executive summary")
    y -= 0.45 * cm

    c.setFont("Helvetica", 10)
    y = draw_wrapped_text(
        c,
        insights.get("executive_summary", ""),
        PAGE_MARGIN_X,
        y,
        max_width=17 * cm,
        line_height=12,
    )
    y -= 0.5 * cm

    y, page_num = draw_bullets(c, "Key insights", insights.get("key_insights", []), PAGE_MARGIN_X, y, page_num)
    y, page_num = draw_bullets(c, "Risks / anomalies", insights.get("risks_anomalies", []), PAGE_MARGIN_X, y, page_num)
    y, page_num = draw_bullets(c, "Recommended actions", insights.get("recommended_actions", []), PAGE_MARGIN_X, y, page_num)
    y, page_num = draw_bullets(c, "Questions to ask", insights.get("questions_to_ask", []), PAGE_MARGIN_X, y, page_num)

    # -------------------------
    # DATA QUALITY
    # -------------------------
    if y < 8 * cm:
        page_num, y = new_page(c, page_num)

    y = draw_section_title(c, "Data Quality Notes", y)

    for note in data_quality_notes:
        if y < PAGE_MARGIN_BOTTOM + 1.5 * cm:
            page_num, y = new_page(c, page_num)

        c.setFont("Helvetica", 10)
        y = draw_wrapped_text(
            c,
            f"- {note}",
            PAGE_MARGIN_X,
            y,
            max_width=17 * cm,
            line_height=12,
        )
        y -= 0.15 * cm

    draw_footer(c, page_num)
    c.save()

    return out_pdf