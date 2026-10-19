from app.validation import currency_label
"""Flow-based, Polish report with embedded fonts and explicit data rules."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from xml.sax.saxutils import escape
import matplotlib
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, CondPageBreak, KeepTogether

WIDTH = A4[0] - 88


def register_fonts():
    root = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    for name, filename in (("AR", "DejaVuSans.ttf"), ("AR-Bold", "DejaVuSans-Bold.ttf")):
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(root / filename)))
    pdfmetrics.registerFontFamily("AR", normal="AR", bold="AR-Bold", italic="AR", boldItalic="AR-Bold")


def money(value):
    if value is None:
        return "N/A"
    rounded = Decimal(value).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
    return f"{abs(rounded) if rounded == 0 else rounded:,.2f}".replace(",", " ").replace(".", ",")


def percent(value):
    if value is None:
        return "N/A"
    rounded = Decimal(value).quantize(Decimal('.1'), rounding=ROUND_HALF_UP)
    return f"{abs(rounded) if rounded == 0 else rounded:+.1f}%".replace(".", ",")


def build_pdf(out_pdf, meta, kpis, comparison, top_categories, insights, chart_paths, decision, data_quality_notes):
    register_fonts()
    Path(out_pdf).parent.mkdir(parents=True, exist_ok=True)
    body = ParagraphStyle("Body", fontName="AR", fontSize=9, leading=13, spaceAfter=6, allowWidows=0, allowOrphans=0, textColor=colors.HexColor("#263646"))
    heading = ParagraphStyle("Heading", parent=body, fontName="AR-Bold", fontSize=13, leading=17, spaceBefore=10, spaceAfter=8, keepWithNext=True)
    long_title = len(meta.get("title", "")) > 90
    title_style = ParagraphStyle("Title", parent=heading, fontSize=18 if long_title else 23, leading=23 if long_title else 29, spaceBefore=0, spaceAfter=14)
    small = ParagraphStyle("Small", parent=body, fontSize=8, leading=11)
    def p(text, style=body):
        return Paragraph(escape(str(text)), style)
    def table(rows, widths):
        t = Table([[p(cell) for cell in row] for row in rows], colWidths=widths, repeatRows=1, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf2f3")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor("#aac5c9")),
            ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#dde4e7")),
        ]))
        return t
    profile = meta.get("profile", {})
    unit=currency_label(profile)
    story = [
        p("AUTO-REPORT / PODSUMOWANIE", small),
        p(meta.get("title", "Raport wartości pozycji"), title_style),
        p(f"Okres raportu: {kpis['start_date']} - {kpis['end_date']}"),
        p(f"Waluta: {profile.get('currency', 'PLN')} | Podstawa kwoty: {profile.get('amount_basis', 'nieokreślona')}"),
        p("Kategorie: " + ("Wszystkie" if meta.get("selected_categories") is None else ", ".join(meta["selected_categories"]))),
        table([[f"Suma pozycji [{unit}]", f"Średnia pozycji [{unit}]", "Liczba pozycji"],
               [money(kpis["total_value"]), money(kpis["avg_value"]), str(kpis["rows_cnt"])]], [WIDTH/3]*3),
        Spacer(1, 8), p(insights["executive_summary"]),
        p("Porównanie okresów", heading),
        p(f"Poprzedni okres: {comparison['previous']['start_date']} - {comparison['previous']['end_date']}"),
        p(comparison["reason"]),
    ]
    if comparison["baseline_available"]:
        story.append(table([["Wskaźnik", "Poprzedni okres", "Różnica", "Zmiana"],
                            [f"Suma [{unit}]", money(comparison["previous"]["total_value"]), money(comparison["difference"]["total_value"]), percent(comparison["change_pct"]["total_value"])],
                            [f"Średnia [{unit}]", money(comparison["previous"]["avg_value"]), money(comparison["difference"]["avg_value"]), percent(comparison["change_pct"]["avg_value"])],
                            ["Liczba pozycji", comparison["previous"]["rows_cnt"], str(comparison["difference"]["rows_cnt"]), percent(comparison["change_pct"]["rows_cnt"])]],
                           [WIDTH*0.30, WIDTH*0.27, WIDTH*0.22, WIDTH*0.21]))
    if decision != comparison["reason"]:
        story.append(p(decision))
    business=meta.get("business",{})
    if any(v is not None for v in business.values()):
        story += [p("Dokumenty i rentowność",heading)]
        labels={"orders":"Unikalne dokumenty w zakresie","quantity":"Ilość ["+profile.get("quantity_unit","")+"]",
                "average_order":"Wartość / dokument ["+unit+"]","cost":"Koszt pozycji ["+unit+"]",
                "profit":"Zysk pozycji ["+unit+"]","margin_pct":"Marża [%]"}
        story.append(table([["Wskaźnik","Wartość"]]+[[label,money(business.get(key))] for key,label in labels.items()],[WIDTH*.67,WIDTH*.33]))
        story.append(p("N/A oznacza brak mapowania, brak wartości w co najmniej jednej pozycji lub brak podstaw do obliczenia. Dokumenty i ich średnia dotyczą pozycji po filtrach. Marża = zysk / wartość sprzedaży; wymaga dodatniej wartości i potwierdzonej semantyki.",small))
    story.append(p("Kontrola danych i reguły", heading))
    story += [p(note) for note in data_quality_notes]
    story += [Spacer(1, 8), p("Struktura wartości pozycji", heading)]
    trend = chart_paths.get("trend")
    if trend:
        story += [p("Wartość według daty", heading), Image(trend, width=WIDTH, height=WIDTH*3.2/9)]
    rows = [["Kategoria", f"Suma [{unit}]"]] + [[r["category"], money(r["total_value"])] for r in top_categories]
    widths = [WIDTH*0.73, WIDTH*0.27]
    category_heading = p("Kategorie - najwyższe sumy i pozostałe", ParagraphStyle("TableHeading", parent=heading, keepWithNext=False))
    # Reserve the heading, column labels and first row, while allowing the rest
    # of a long table to use the current page and repeat its labels on the next.
    first_rows_height = table(rows[:2], widths).wrap(WIDTH, 10000)[1]
    heading_height = category_heading.wrap(WIDTH, 10000)[1] + heading.spaceBefore + heading.spaceAfter
    story += [CondPageBreak(first_rows_height + heading_height), category_heading, table(rows, widths)]
    story += [Spacer(1, 8), p("Tabela obejmuje do 10 kategorii oraz sumę pozostałych. Razem odpowiada wartości po filtrach.", small),
              p("Średnia zaokrąglona do 0,01 jednostki metodą HALF_UP. Sumy liczone w całkowitych setnych jednostki.", small)]
    source_range = meta.get("source_range", {})
    story += [KeepTogether([p(f"Zakres dat w pliku: {source_range.get('min_date', '')} - {source_range.get('max_date', '')}", small),
              p("Zakres dat występujących w pliku nie dowodzi kompletności eksportu.", small),
              p(f"SHA-256 źródła: {meta.get('source_sha256', '')}", small)])]
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#c4d3d7"))
        canvas.line(44, 39, A4[0]-44, 39)
        canvas.setFont("AR", 7)
        canvas.drawString(44, 26, "Auto-Report 0.2.0 | Szablon 4 | " + meta.get("run_id", ""))
        canvas.drawRightString(A4[0]-44, 26, f"Strona {doc.page}")
        canvas.restoreState()
    SimpleDocTemplate(out_pdf, pagesize=A4, leftMargin=44, rightMargin=44, topMargin=38, bottomMargin=52,
                      title=meta.get("title", "Auto-Report"), author="Auto-Report").build(story, onFirstPage=footer, onLaterPages=footer)
    return out_pdf
