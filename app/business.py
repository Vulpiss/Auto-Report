"""Optional business metrics; missing mapped values never become zero."""
from collections import defaultdict
from decimal import Decimal
from app.validation import parse_minor
OPTIONAL = {"quantity_col":"quantity","order_col":"order_id","product_col":"product","customer_col":"customer","cost_col":"cost_minor","profit_col":"profit_minor"}

class OptionalValidationError(ValueError):
    def __init__(self, problems, result, missing, adjustments):
        self.problems = problems
        self.result, self.missing, self.adjustments = result, missing, adjustments
        super().__init__("; ".join(f"{column}: {message}" for column, _, message in problems))


def _parse_optional_value(text, key, profile):
    import re
    if key == "quantity":
        if not re.fullmatch(r"[+-]?\d+(?:[.,]\d{1,6})?", text):
            raise ValueError("Niepoprawna ilość.")
        if profile.decimal_separator == "." and "," in text or profile.decimal_separator == "," and "." in text:
            raise ValueError("Separator ilości nie pasuje do profilu.")
        value = Decimal(text.replace(",", "."))
        if abs(value) > 10**10 or value < 0 and not profile.allow_negative:
            raise ValueError("Ilość poza zakresem lub niedopuszczalna ilość ujemna.")
        return value
    if key.endswith("_minor"):
        return parse_minor(text, profile.decimal_separator,
                           True if key == "profit_minor" else profile.allow_negative, profile.amount_precision)
    if len(text) > 200 or any(ord(c) < 32 for c in text):
        raise ValueError("Identyfikator: do 200 znaków, bez znaków sterujących.")
    return text


def parse_optional(record, profile):
    result, missing, adjustments = {}, [], {}
    problems = []
    for setting, key in OPTIONAL.items():
        column = getattr(profile, setting)
        if not column:
            continue
        raw = record.get(column)
        text = "" if raw is None else str(raw).strip()
        if not text:
            result[key] = None
            missing.append(key)
        else:
            try:
                result[key] = _parse_optional_value(text, key, profile)
                if key.endswith("_minor"):
                    adjustments[key] = str(Decimal(result[key])/100-Decimal(text.replace(profile.decimal_separator,".")))
            except ValueError as exc:
                problems.append((column, text, str(exc)))
    if problems:
        raise OptionalValidationError(problems, result, missing, adjustments)
    return result, missing, adjustments

def metrics(rows, profile):
    def full(key):
        return bool(rows) and all(r.get(key) is not None for r in rows)
    total = Decimal(sum(r["value_minor"] for r in rows))/100
    orders = len({r["order_id"] for r in rows}) if full("order_id") else None
    quantity = sum((r["quantity"] for r in rows),Decimal(0)) if full("quantity") else None
    cost = Decimal(sum(r["cost_minor"] for r in rows))/100 if full("cost_minor") else None
    profit = Decimal(sum(r["profit_minor"] for r in rows))/100 if full("profit_minor") else total-cost if cost is not None and profile.value_is_sales else None
    return dict(orders=orders,quantity=quantity,cost=cost,profit=profit,
        average_order=total/orders if orders else None,
        margin_pct=100*profit/total if profit is not None and total>0 and profile.value_is_sales else None)

def contributions(current, previous, field, available):
    groups=defaultdict(lambda:[0,0,0])
    for index,rows in enumerate((current,previous)):
        for row in rows:
            # None is distinct from a literal customer/product named "(brak)".
            key=row.get(field)
            groups[key][index]+=row["value_minor"]
            groups[key][2]+=index==0
    return sorted([dict(entity=key,current=Decimal(v[0])/100,previous=Decimal(v[1])/100 if available else None,
                        difference=Decimal(v[0]-v[1])/100 if available else None,rows=v[2])
                   for key,v in groups.items()],key=lambda x:(-abs(x["difference"] or 0),str(x["entity"])))

def business_notes(result):
    b=result.get("business")
    if not b:return []
    from app.pdf_report import money
    unit=result["profile"]["currency"]
    labels={"orders":"Unikalne dokumenty w wybranym zakresie","quantity":"Ilość (jednostka zadeklarowana w profilu)","cost":"Koszt pozycji","profit":"Zysk pozycji","average_order":"Wartość na dokument w wybranym zakresie","margin_pct":"Marża %"}
    notes=[f"{label}: {money(b[key])}"+(" "+unit if key in ("cost","profit","average_order") else "") for key,label in labels.items()]
    notes.append("Unikalne dokumenty liczone po identyfikatorze mogą obejmować korekty i anulowania; nie są liczbą zrealizowanych zamówień.")
    notes.append("N/A oznacza brak mapowania, brak wartości w co najmniej jednej pozycji lub brak podstaw do obliczenia. Dokumenty i ich średnia dotyczą wyłącznie pozycji po filtrach.")
    return notes
