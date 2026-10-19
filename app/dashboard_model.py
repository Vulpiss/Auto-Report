from app.validation import currency_label
"""Presentation-ready data shared by screen charts and slide rendering."""
from collections import defaultdict
from datetime import date, timedelta
import calendar
from decimal import Decimal
from app.pdf_report import money, percent
from app.analysis import ranked_categories, aggregate_label

VIEW_NAMES = ("Wynik i trend", "Kategorie i źródła zmiany", "Jakość i pokrycie danych")
COLORS = ("#2786e2", "#21a4a4", "#dba752", "#8a79c7", "#8498ad")

def make_model(result, grouping="Dzień"):
    if grouping not in ("Dzień", "Tydzień", "Miesiąc"):
        raise ValueError("Nieobsługiwane grupowanie.")
    unit=currency_label(result["profile"])
    daily = result["daily"]
    groups = defaultdict(list)
    for i, item in enumerate(daily):
        day = date.fromisoformat(item["event_date"])
        key = day if grouping == "Dzień" else day.replace(day=1) if grouping == "Miesiąc" else day - timedelta(days=day.weekday())
        groups[key].append(i)
    trend = []
    day_to_bucket = {}
    available = result["comparison"]["baseline_available"]
    for number, indices in enumerate(groups.values()):
        items = [daily[i] for i in indices]
        previous = [result["previous_daily"][i] for i in indices]
        value = sum((r["total_value"] for r in items), Decimal(0)) if all(r["total_value"] is not None for r in items) else None
        old = sum((r["total_value"] for r in previous), Decimal(0)) if available else None
        label = items[0]["event_date"]
        end = items[-1]["event_date"]
        trend.append(dict(label=label if label == end else label+" / "+end,
                          previous_label=previous[0]["event_date"]+" / "+previous[-1]["event_date"],
                          current=value, previous=old, rows_cnt=sum(r["rows_cnt"] for r in items),
                          state="Brak potwierdzonej kompletności" if value is None else
                          "Częściowy miesiąc" if grouping == "Miesiąc" and len(items) < calendar.monthrange(date.fromisoformat(label).year,date.fromisoformat(label).month)[1] else "Częściowy tydzień" if grouping == "Tydzień" and len(items) < 7 else "Dostępne pozycje"))
        for i in indices:
            day_to_bucket[daily[i]["event_date"]] = number
    cats = result["categories"]
    # Stable category order/colors are shared by all charts for this snapshot.
    names = [c["category"] for c in cats[:4]]
    has_rest = len(cats) > 4
    labels = names + ([aggregate_label((c["category"] for c in cats), "Pozostałe kategorie (grupa)")] if has_rest else [])
    # Group identity is numeric, so a source category with the same label cannot merge with it.
    buckets = defaultdict(int)
    for row in result["rows"]:
        ci = names.index(row["category"]) if row["category"] in names else 4
        buckets[(day_to_bucket[row["event_date"]],ci,row["value_minor"] < 0)] += row["value_minor"]
    structure = []
    for bucket, t in enumerate(trend):
        for ci, name in enumerate(labels):
            for negative in (False,True):
                minor = buckets[(bucket,ci,negative)]
                structure.append(dict(label=t["label"], category=name, category_id=ci,
                                      sign="Ujemne" if negative else "Dodatnie",
                                      value=Decimal(minor)/100 if t["current"] is not None else None))
    changes = sorted(cats,key=lambda r: -abs(r["difference"] or 0))
    top_changes = [dict(category=r["category"], value=r["difference"]) for r in changes[:5]]
    if len(changes)>5:
        top_changes.append(dict(category=aggregate_label((c["category"] for c in cats), "Pozostałe (grupa)"),value=sum((r["difference"] for r in changes[5:]),Decimal(0)) if available else None))
    table = []
    for c in cats:
        table.append(dict(category=c["category"], value=c["total_value"], previous=c["previous"]["total_value"] if available else None,
                          difference=c["difference"], change=c["change_pct"], rows_cnt=c["rows_cnt"],
                          avg=c["avg_value"]))
    k, cmp, q = result["kpis"], result["comparison"], result["quality"]
    cards = [
        [(f"Wartość pozycji · {unit}",money(k["total_value"]), "Poprzednio "+money(cmp["previous"]["total_value"])+f" {unit}" if available else "Porównanie niedostępne",percent(cmp["change_pct"]["total_value"])),
         ("Liczba pozycji",str(k["rows_cnt"]),"Poprzednio "+str(cmp["previous"]["rows_cnt"]) if available else "Porównanie niedostępne",percent(cmp["change_pct"]["rows_cnt"])),
         (f"Średnia pozycji · {unit}",money(k["avg_value"]),"Poprzednio "+money(cmp["previous"]["avg_value"])+f" {unit}" if available else "Porównanie niedostępne",percent(cmp["change_pct"]["avg_value"]))],
        [(f"Zmiana wartości · {unit}",money(cmp["difference"]["total_value"]),"Różnica między okresami",percent(cmp["change_pct"]["total_value"])),
         (f"Największy wkład · {unit}",money(changes[0]["difference"]) if changes else "N/A",changes[0]["category"] if changes and available else "Porównanie niedostępne",""),
         ("Kategorie w analizie",str(len(cats)),"Suma zbiorów obu okresów","")],
        [("Rekordy w źródle",str(q["total_rows"]),str(q["rows_in_period"])+" po filtrach",""),
         ("Powtórzenia / ujemne",str(q["duplicate_rows"])+" / "+str(q["negative_values"]),"W całym źródle",""),
         ("Pełny zakres bieżący","Zadeklarowany" if result["coverage_current"] else "Niepotwierdzony","Deklaracja użytkownika","")]
    ]
    return dict(trend=trend,structure=structure,category_labels=labels,changes=top_changes,
                rank=ranked_categories(result,5),table=table,cards=cards,grouping=grouping,
                bucket_dates=[[daily[i]["event_date"] for i in indices] for indices in groups.values()])


def table_page(result, model, offset=0, limit=100):
    """Compute sparklines only for visible categories, preserving full aggregates."""
    if type(offset) is not int or offset < 0 or type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("Niepoprawny zakres strony tabeli.")
    rows = []
    for item in model["table"][offset:offset + limit]:
        values = result["category_daily"].get(item["category"], {})
        spark = [sum(values.get(day, 0) for day in dates) / 100
                 if trend["current"] is not None else None
                 for dates, trend in zip(model["bucket_dates"], model["trend"])]
        rows.append(dict(item, spark=spark))
    return rows
