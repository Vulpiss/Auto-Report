"""Local analysis shared by dashboard and PDF. Money never uses binary floats."""
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from app.validation import CsvProfile, load_csv
from app.queries import _period, compute_previous_period
from app.data_quality import build_quality_notes


def earliest_reporting_date(end):
    """Inclusive trailing five calendar years; clamp a leap anniversary to Feb 28."""
    try:
        anniversary = end.replace(year=end.year - 5)
    except ValueError:
        anniversary = end.replace(year=end.year - 5, day=28)
    return anniversary + timedelta(days=1)


def select_reporting_period(max_date, days):
    if type(days) is not int or days < 1:
        raise ValueError("Okres musi obejmować co najmniej 1 dzień i maksymalnie 5 lat kalendarzowych.")
    end = date.fromisoformat(max_date)
    if days > (end - earliest_reporting_date(end)).days + 1:
        raise ValueError("Maksymalny okres raportu to 5 lat kalendarzowych.")
    return (end - timedelta(days=days - 1)).isoformat(), end.isoformat()


def summary(rows, start, end):
    count = len(rows)
    total = sum(r['value_minor'] for r in rows)
    return dict(rows_cnt=count, total_minor=total, total_value=Decimal(total) / 100,
                avg_value=(Decimal(total) / (100 * count)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP) if count else None,
                start_date=start, end_date=end)


def exact_values(kpi):
    return dict(total_value=kpi['total_value'], rows_cnt=Decimal(kpi['rows_cnt']),
                avg_value=Decimal(kpi['total_minor']) / (100 * kpi['rows_cnt']) if kpi['rows_cnt'] else None)


def delta(current, previous, available):
    c, p = exact_values(current), exact_values(previous)
    absolute, percent = {}, {}
    for key in c:
        ok = available and c[key] is not None and p[key] is not None
        absolute[key] = c[key] - p[key] if ok else None
        percent[key] = 100 * (c[key] - p[key]) / p[key] if ok and p[key] > 0 else None
    return absolute, percent


def analyze(source, *, profile=None, days=7, **filters):
    profile = profile or CsvProfile()
    return analyze_parsed(load_csv(source, profile), profile=profile, days=days, **filters)


def analyze_parsed(parsed, *, profile=None, days=7, start_date=None, end_date=None,
                   categories=None, coverage_start=None, coverage_end=None, comparison_mode="Poprzedni okres", products=None, customers=None):
    profile = profile or CsvProfile()
    rows = parsed.rows
    source_range = dict(min_date=min(r['event_date'] for r in rows), max_date=max(r['event_date'] for r in rows))
    if bool(start_date) != bool(end_date):
        raise ValueError('Podaj początek i koniec okresu raportu.')
    if not start_date:
        start_date, end_date = select_reporting_period(source_range['max_date'], days)
    a, b = _period(start_date, end_date)
    if a.date() < earliest_reporting_date(b.date()):
        raise ValueError('Maksymalny okres raportu to 5 lat kalendarzowych.')
    if bool(coverage_start) != bool(coverage_end):
        raise ValueError('Podaj obie granice kompletnego eksportu.')
    if coverage_start:
        _period(coverage_start, coverage_end)
        if source_range['min_date'] < coverage_start or source_range['max_date'] > coverage_end:
            raise ValueError('Dane wychodzą poza zadeklarowany zakres eksportu.')
    options = sorted({r['category'] for r in rows})
    selected = None if categories is None else set(categories)
    if selected is not None and not selected.issubset(options):
        raise ValueError('Wybrano kategorię nieobecną w źródle.')
    ps, pe = compute_previous_period(start_date, end_date)
    if comparison_mode == "Rok do roku":
        def last_year(value):
            d=date.fromisoformat(value)
            try:return d.replace(year=d.year-1).isoformat()
            except ValueError:return d.replace(year=d.year-1,day=28).isoformat()
        ps,pe=last_year(start_date),last_year(end_date)
        if (date.fromisoformat(pe)-date.fromisoformat(ps)).days != (b-a).days:
            raise ValueError("Rok do roku: zakresy mają różną liczbę dni przez 29 lutego. Wybierz zakres bez 29 lutego lub poprzedni okres.")
    elif comparison_mode != "Poprzedni okres":
        raise ValueError("Nieobsługiwane porównanie.")
    for field,selection in (("product",products),("customer",customers)):
        if selection is not None and not set(selection).issubset({r.get(field) for r in rows}):
            raise ValueError("Filtr produktu lub klienta nie pasuje do źródła.")

    current, previous = [], []
    outside = excluded = 0
    for row in rows:
        inside = start_date <= row['event_date'] <= end_date
        accepted = (selected is None or row["category"] in selected) and (products is None or row.get("product") in products) and (customers is None or row.get("customer") in customers)
        outside += not inside
        excluded += inside and not accepted
        if accepted:
            if inside:
                current.append(row)
            if ps <= row['event_date'] <= pe:
                previous.append(row)
    kpis, prev = summary(current, start_date, end_date), summary(previous, ps, pe)
    verified = bool(coverage_start and coverage_start <= ps and coverage_end >= end_date)
    available = bool(verified and current and previous)
    reason = ('Nie potwierdzono pełnego eksportu dla obu okresów.' if not verified else
              'Jeden z okresów nie zawiera pozycji po filtrach.' if not current or not previous else
              'Zakres eksportu potwierdzony przez użytkownika; baza 0 lub ujemna daje N/A.')
    differences, changes = delta(kpis, prev, available)
    comparison = dict(mode=comparison_mode,current=kpis, previous=prev, baseline_available=available,
                      coverage_verified=verified, reason=reason, change_pct=changes, difference=differences)
    groups, old_groups, by_day = defaultdict(list), defaultdict(list), defaultdict(list)
    for row in current:
        groups[row['category']].append(row)
        by_day[row['event_date']].append(row)
    for row in previous:
        old_groups[row['category']].append(row)
    cats = []
    for name in groups.keys() | old_groups.keys():
        c, p = summary(groups[name], start_date, end_date), summary(old_groups[name], ps, pe)
        diff, pct = delta(c, p, available)
        cats.append(dict(category=name, **c, previous=p, difference=diff['total_value'], change_pct=pct['total_value']))
    cats.sort(key=lambda r: (-r['total_minor'], r['category']))
    daily = []
    complete_current = bool(coverage_start and coverage_start <= start_date and coverage_end >= end_date)
    day = a.date()
    while day <= b.date():
        key = day.isoformat()
        bucket = by_day[key]
        item = summary(bucket, key, key)
        daily.append(dict(event_date=key, total_value=item['total_value'] if bucket or complete_current else None,
                          total_minor=item['total_minor'], rows_cnt=len(bucket),
                          state='Pozycje' if bucket else 'Brak pozycji' if complete_current else 'Brak danych o kompletności'))
        day += timedelta(days=1)
    old_by_day = defaultdict(list)
    for row in previous:
        old_by_day[row['event_date']].append(row)
    previous_daily = []
    for index in range(len(daily)):
        key = (date.fromisoformat(ps) + timedelta(days=index)).isoformat()
        bucket = old_by_day[key]
        total = sum(x['value_minor'] for x in bucket)
        previous_daily.append(dict(event_date=key, total_minor=total, rows_cnt=len(bucket),
                                   total_value=Decimal(total)/100 if verified else None))
    category_daily = defaultdict(lambda: defaultdict(int))
    for row in current:
        category_daily[row['category']][row['event_date']] += row['value_minor']
    quality = dict(parsed.quality, rows_in_period=len(current), rows_outside_period=outside,
                   rows_excluded_category=excluded, view_negative_count=sum(r['value_minor'] < 0 for r in current),
                   view_negative_minor=sum(r['value_minor'] for r in current if r['value_minor'] < 0))
    quality["view_rounded_rows"] = sum(Decimal(r.get("rounding_delta","0")) != 0 for r in current)
    quality["view_rounding_delta"] = str(sum((Decimal(r.get("rounding_delta","0")) for r in current), Decimal(0)))
    notes = build_quality_notes(quality) + [
        f"Po filtrach: {len(current)}. Poza datami: {outside}. Wykluczone filtrami w okresie: {excluded}.",
        'Daty bez pozycji nie są automatycznie uznawane za dni ze sprzedażą równą zero.',
        f'Waluta: {profile.currency}. Podstawa kwoty: {profile.amount_basis}.',
    ]
    if profile.currency == "XXX":
        notes.append("Waluta nieokreślona. j.p. oznacza jednostki pieniężne źródła; bez przeliczania walut.")
    if profile.amount_precision == "half_up":
        notes.append(f"Zaokrąglanie HALF_UP każdej pozycji do 2 miejsc: {quality['rounded_rows']} zmienionych w źródle; wpływ {quality['rounding_delta']} jednostki. W widoku: {quality['view_rounded_rows']}; wpływ {quality['view_rounding_delta']}.")
    if not complete_current:
        notes.append('Nie potwierdzono kompletności bieżącego okresu. Suma dotyczy dostępnych pozycji.')
    if profile.amount_basis == 'nieokreślona':
        notes.append('Nie określono netto/brutto. Suma nie jest automatycznie miarą przychodu.')
    if profile.value_mode == "unit_price":
        notes.append("Wartość pozycji = cena jednostkowa × ilość; zaokrąglanie dopiero po mnożeniu.")
    if " " in profile.date_format:
        notes.append("Godzina pominięta przy grupowaniu. Data lokalna ze źródła; bez konwersji stref czasowych.")
    from app.business import metrics,contributions,business_notes
    business=metrics(current,profile)
    previous_business=metrics(previous,profile) if available else None
    dimensions={field:contributions(current,previous,field,available) for field in ("product","customer") if getattr(profile,field+"_col")}
    field_names={"quantity":"ilość","order_id":"dokument","product":"produkt","customer":"klient","cost_minor":"koszt pozycji","profit_minor":"zysk pozycji"}
    missing=parsed.quality.get("optional_missing",{})
    optional_notes=["Braki w dodatkowych kolumnach źródła: "+("; ".join(f"{field_names[k]}: {v}" for k,v in missing.items()) or "nie wykryto")+".",
                    f"Jednostka ilości: {profile.quantity_unit or 'nie podano'}. Koszt/zysk oznacza kwotę całej pozycji, nie jednostki."]
    for field,adjustment in parsed.quality.get("optional_rounding",{}).items():
        if adjustment["rows"]:
            optional_notes.append(f"Zaokrąglenia — {field_names[field]}: {adjustment['rows']} pozycji; wpływ na sumę {adjustment['delta']} jednostki źródła.")
    if products is not None or customers is not None:notes.append(f"Filtr produktów: {products}; filtr klientów: {customers}.")
    notes+=optional_notes if any(getattr(profile,k) for k in ("quantity_col","order_col","cost_col","profit_col","product_col","customer_col")) else []

    return dict(business=business,previous_business=previous_business,dimensions=dimensions,
                selected_products=products,selected_customers=customers,comparison_mode=comparison_mode,
                kpis=kpis, comparison=comparison, categories=cats, daily=daily, rows=current,
                previous_daily=previous_daily, category_daily={k:dict(v) for k,v in category_daily.items()},
                coverage_current=complete_current,
                quality=quality, notes=notes, profile=profile.to_dict(), source_range=source_range,
                source_sha256=parsed.source_sha256, coverage_start=coverage_start, coverage_end=coverage_end,
                selected_categories=None if selected is None else sorted(selected), category_options=options,
                status='complete' if current else 'empty')


def weekly_trend(daily):
    groups = defaultdict(list)
    for item in daily:
        day = date.fromisoformat(item['event_date'])
        groups[day - timedelta(days=day.weekday())].append(item)
    return [dict(event_date=items[0]['event_date'], end_date=items[-1]['event_date'],
                 total_value=sum((i['total_value'] for i in items), Decimal(0)) if all(i['total_value'] is not None for i in items) else None,
                 rows_cnt=sum(i['rows_cnt'] for i in items),
                 state='Częściowy tydzień' if len(items) < 7 else 'Pełny tydzień')
            for _, items in sorted(groups.items())]


def aggregate_label(names, base):
    """Keep synthetic group labels distinct from every source category."""
    used = set(names)
    label = base
    number = 1
    while label in used:
        label = f"{base} [suma {number}]"
        number += 1
    return label


def ranked_categories(result, limit=5):
    categories = [r for r in result['categories'] if r['rows_cnt']]
    top = [dict(r) for r in categories[:limit]]
    rest = categories[limit:]
    if rest:
        total = sum(r['total_minor'] for r in rest)
        top.append(dict(category=aggregate_label((r['category'] for r in result['categories']), f'Pozostałe ({len(rest)} kategorii)'), total_minor=total,
                        total_value=Decimal(total) / 100))
    return top
