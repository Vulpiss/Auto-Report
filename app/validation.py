"""Shared CSV contract. No guessing or silent row removal; rounding is opt-in."""
import csv
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import hashlib
import io
import math
import re
from app.import_diagnostics import problem, diagnostic_quality

MAX_BYTES = 100 * 1024 * 1024
MAX_ROWS = 1_000_000
MAX_MINOR = 10**12
CURRENCIES = ("PLN", "USD", "EUR", "GBP", "XXX")
DATE_FORMATS = ("%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y", "%d/%m/%Y", "%m/%d/%Y %H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S")
ENCODINGS = ("utf-8-sig", "cp1250", "cp1252")

def currency_label(profile):
    code = profile.get("currency", "PLN") if isinstance(profile, dict) else profile.currency
    return "j.p." if code == "XXX" else code



class DataValidationError(ValueError):
    def __init__(self, message, quality=None):
        super().__init__(message)
        self.quality = quality or {}


@dataclass(frozen=True)
class CsvProfile:
    date_col: str = "date"
    value_col: str = "value"
    category_col: str = "category"
    delimiter: str = ","
    encoding: str = "utf-8-sig"
    date_format: str = "%Y-%m-%d"
    decimal_separator: str = "."
    allow_negative: bool = False
    currency: str = "PLN"
    amount_basis: str = "nieokreślona"
    amount_precision: str = "strict"

    quantity_col: str = ""
    order_col: str = ""
    product_col: str = ""
    customer_col: str = ""
    cost_col: str = ""
    profit_col: str = ""
    value_is_sales: bool = False
    quantity_unit: str = ""

    value_mode: str = "amount"

    def validate(self):
        if self.value_mode not in ("amount", "unit_price") or (self.value_mode == "unit_price" and not self.quantity_col):
            raise DataValidationError("Cena jednostkowa wymaga kolumny ilości.")
        optional = (self.quantity_col,self.order_col,self.product_col,self.customer_col,self.cost_col,self.profit_col)
        if any(not isinstance(x,str) for x in optional):
            raise DataValidationError("Nazwy kolumn muszą być tekstem.")
        names = (self.date_col, self.value_col, self.category_col) + tuple(x for x in optional if x)
        if self.cost_col and self.profit_col:
            raise DataValidationError("Wybierz koszt pozycji albo zysk pozycji, nie oba.")
        if type(self.value_is_sales) is not bool or not isinstance(self.quantity_unit,str) or len(self.quantity_unit)>40 or any(ord(c)<32 for c in self.quantity_unit):
            raise DataValidationError("Niepoprawna deklaracja sprzedaży lub jednostki ilości.")
        if self.quantity_col and not self.quantity_unit.strip():
            raise DataValidationError("Podaj wspólną jednostkę ilości, np. szt.")

        if any(not isinstance(n, str) or not n.strip() for n in names) or len(set(names)) != len(names):
            raise DataValidationError("Wybierz trzy różne, niepuste nazwy kolumn.")
        if self.delimiter not in (",", ";", "\t"):
            raise DataValidationError("Separator CSV musi być przecinkiem, średnikiem lub tabulatorem.")
        if self.encoding not in ENCODINGS:
            raise DataValidationError("Obsługiwane kodowania: UTF-8, Windows-1250 i Windows-1252.")
        if self.date_format not in DATE_FORMATS:
            raise DataValidationError("Wybierz obsługiwany jawny format daty; nie rozpoznajemy kolejności dnia i miesiąca automatycznie.")
        if self.decimal_separator not in (".", ","):
            raise DataValidationError("Wybierz separator dziesiętny.")
        if self.currency not in CURRENCIES or self.amount_basis not in ("netto", "brutto", "nieokreślona"):
            raise DataValidationError("Wybierz jedną walutę profilu i podstawę netto/brutto/nieokreśloną.")
        if self.amount_precision not in ("strict", "half_up"):
            raise DataValidationError("Wybierz ścisłą precyzję lub jawne zaokrąglanie HALF_UP.")
        if type(self.allow_negative) is not bool:
            raise DataValidationError("Reguła kwot ujemnych musi być wartością logiczną.")

    def to_dict(self):
        return asdict(self)


@dataclass
class ParsedData:
    rows: list
    quality: dict
    source_sha256: str


def parse_date(value, date_format="%Y-%m-%d"):
    text = str(value).strip()
    if " " in date_format and date_format in DATE_FORMATS:
        return datetime.strptime(text, date_format).date().isoformat()
    shape = r"\d{4}-\d{2}-\d{2}" if date_format == "%Y-%m-%d" else r"\d{2}\.\d{2}\.\d{4}"
    if date_format in ("%m/%d/%Y", "%d/%m/%Y"):
        shape = r"\d{1,2}/\d{1,2}/\d{4}"
    if date_format not in DATE_FORMATS or not re.fullmatch(shape, text):
        raise ValueError("data nie pasuje do wybranego formatu")
    return datetime.strptime(text, date_format).date().isoformat()


def parse_minor(value, decimal_separator=".", allow_negative=False, amount_precision="strict"):
    text = str(value).strip()
    decimal = re.escape(decimal_separator)
    digits = 2 if amount_precision == "strict" else 12
    if amount_precision not in ("strict", "half_up"):
        raise ValueError("Nieobsługiwana reguła precyzji.")
    if not re.fullmatch(r"[+-]?\d+(?:" + decimal + r"\d{1," + str(digits) + r"})?", text):
        raise ValueError(f"kwota wymaga liczby z maksymalnie {digits} miejscami, bez separatora tysięcy")
    try:
        number = Decimal(text.replace(decimal_separator, "."))
        if not number.is_finite() or abs(number) > Decimal(MAX_MINOR) / 100:
            raise ValueError("kwota poza obsługiwanym zakresem")
        if number < 0 and not allow_negative:
            raise ValueError("kwota ujemna wymaga jawnego dopuszczenia w profilu")
        return int(number.quantize(Decimal(".01"), rounding=ROUND_HALF_UP) * 100)
    except InvalidOperation as exc:
        raise ValueError("niepoprawna kwota") from exc


def repair_hint(kind, profile):
    if kind == "event_date":
        example = datetime(2026, 10, 2, 14, 30).strftime(profile.date_format)
        return f"Sprawdź datę w źródle i format w ustawieniach. Wybrany zapis: {example}."
    if kind in ("value_minor", "cost_minor", "profit_minor"):
        example = "123" + profile.decimal_separator + "45"
        return f"Sprawdź kwotę w źródle. Wybrany zapis: {example}, bez separatora tysięcy. Sprawdź regułę precyzji i kwot ujemnych."
    if kind == "quantity":
        return "Sprawdź ilość w źródle, separator dziesiętny oraz wspólną jednostkę ilości w ustawieniach."
    if kind == "category":
        return "Uzupełnij kategorię w źródle; etykieta może mieć do 200 znaków, bez znaków sterujących."
    return "Sprawdź identyfikator lub nazwę w źródle: do 200 znaków, bez znaków sterujących."


@dataclass(frozen=True)
class InvalidCsvRecord:
    message: str
    hint: str


def inspect_records(records, profile, progress=None):
    profile.validate()
    from app.business import OPTIONAL, OptionalValidationError, parse_optional
    optional_columns = {field: getattr(profile, setting) for setting, field in OPTIONAL.items()}
    impacts = {"quantity": "ilość", "order_id": "liczba dokumentów i wartość na dokument",
               "cost_minor": "koszt, zysk wyliczany z kosztu i marża", "profit_minor": "zysk i marża",
               "product": "pełny podział według produktów", "customer": "pełny podział według klientów"}
    optional_hints = {key: f"Uzupełnij pole w źródle, jeśli potrzebujesz wskaźnika: {impact}. Brak nie staje się zerem."
                      for key, impact in impacts.items()}
    quality = {"total_rows": 0, "valid_rows": 0, "invalid_rows": 0,
               "exact_duplicate_rows": 0, "blank_lines": 0, "duplicate_rows": 0, "negative_values": 0, "issues": [],
               "rounded_rows": 0, "rounding_delta": "0", "optional_missing": {}, "optional_rounding": {},
               "warnings": [], "scan_complete": True}
    rows, seen, exact_seen = [], set(), set()
    for source_line, record in records:
        line_end = source_line
        if isinstance(source_line, tuple):
            source_line, line_end = source_line
        quality["total_rows"] += 1
        if progress and quality["total_rows"] % 10000 == 0:
            progress(quality["total_rows"])
        if quality["total_rows"] > MAX_ROWS:
            quality["scan_complete"] = False
            p = problem(source_line, "Cały wiersz", "", f"Przekroczono limit {MAX_ROWS} rekordów.",
                        "Wyeksportuj mniejszy zakres danych.", line_end=line_end)
            quality["issues"].append(dict(line=source_line, reasons=[p["problem"]], problems=[p]))
            raise DataValidationError(f"Limit wynosi {MAX_ROWS} rekordów.", quality)
        if isinstance(record, InvalidCsvRecord):
            p = problem(source_line, "Cały wiersz", "", record.message, record.hint, line_end=line_end)
            quality["invalid_rows"] += 1
            quality["issues"].append(dict(line=source_line, reasons=[record.message], problems=[p]))
            continue
        exact_key = hashlib.sha256(repr(tuple(record.items())).encode("utf-8")).digest()
        if exact_key in exact_seen: quality["exact_duplicate_rows"] += 1
        exact_seen.add(exact_key)
        details = []
        def add_issue(column, value, message, kind):
            details.append(problem(source_line, column, value, message, repair_hint(kind, profile), line_end=line_end))

        try:
            extra, missing, adjustments = parse_optional(record, profile)
        except OptionalValidationError as exc:
            extra, missing, adjustments = exc.result, exc.missing, exc.adjustments
            for column, value, message in exc.problems:
                kind = next(key for key, name in optional_columns.items() if name == column)
                add_issue(column, value, message, kind)
        original = None
        if profile.value_mode == "unit_price":
            try:
                price_text = str(record.get(profile.value_col, "")).strip()
                shape = r"[+-]?\d+(?:" + re.escape(profile.decimal_separator) + r"\d{1,6})?"
                if not re.fullmatch(shape, price_text): raise ValueError("Niepoprawna cena jednostkowa.")
                price = Decimal(price_text.replace(profile.decimal_separator, "."))
                if abs(price) > Decimal(MAX_MINOR)/100 or (price < 0 and not profile.allow_negative):
                    raise ValueError("Cena jednostkowa poza zakresem.")
                if extra.get("quantity") is not None:
                    original = price * extra["quantity"]
            except ValueError as exc:
                add_issue(profile.value_col, record.get(profile.value_col), str(exc), "value_minor")
            if extra.get("quantity") is None and not any(p["column"] == profile.quantity_col for p in details):
                add_issue(profile.quantity_col, record.get(profile.quantity_col), "Brak ilości do obliczenia wartości cena × ilość.", "quantity")

        parsed = {}
        for name, key, parser in (
            (profile.date_col, "event_date", lambda v: parse_date(v, profile.date_format)),
            (profile.value_col, "value_minor", lambda v: parse_minor(v, profile.decimal_separator, profile.allow_negative, profile.amount_precision)),
            (profile.category_col, "category", lambda v: str(v).strip()),
        ):
            if key == "value_minor" and profile.value_mode == "unit_price" and original is None:
                continue
            value = str(original).replace(".", profile.decimal_separator) if key == "value_minor" and original is not None else record.get(name)
            if value is None or (isinstance(value, float) and math.isnan(value)) or str(value).strip() == "":
                add_issue(name, value, "Brak wartości wymaganej.", key)
                continue
            try:
                parsed[key] = parser(value)
                if key == "category" and (len(parsed[key]) > 200 or any(ord(c) < 32 for c in parsed[key])):
                    raise ValueError("kategoria: maksymalnie 200 znaków, bez znaków sterujących")
            except (ValueError, TypeError) as exc:
                message = "Niepoprawna data lub format daty." if key == "event_date" else str(exc)
                if key == "value_minor" and profile.value_mode == "unit_price":
                    message = "Wartość cena × ilość: " + message
                add_issue(name, record.get(name), message, key)
        parsed.update(extra)
        parsed["source_line"] = source_line
        parsed["optional_adjustments"] = adjustments
        for key in missing:quality["optional_missing"][key]=quality["optional_missing"].get(key,0)+1
        for key,value in adjustments.items():
            entry=quality["optional_rounding"].setdefault(key,{"rows":0,"delta":"0"})
            entry["rows"]+=Decimal(value)!=0
            entry["delta"]=str(Decimal(entry["delta"])+Decimal(value))
        if missing:
            warnings = []
            for key in missing:
                if key == "quantity" and profile.value_mode == "unit_price":
                    continue  # The missing quantity already has a blocking problem.
                column = optional_columns[key]
                warnings.append(problem(source_line, column, record.get(column), "Brak wartości w kolumnie dodatkowej.", optional_hints[key],
                                        warning=True, line_end=line_end))
            if warnings:
                quality["warnings"].append(dict(line=source_line, problems=warnings))
        if details:
            quality["invalid_rows"] += 1
            quality["issues"].append({"line": source_line, "reasons": [f"{p['column']}: {p['problem']}" for p in details], "problems": details})
            continue
        if original is None:
            original = Decimal(str(record[profile.value_col]).strip().replace(profile.decimal_separator, "."))
        adjustment = Decimal(parsed["value_minor"]) / 100 - original
        parsed["rounding_delta"] = str(adjustment)
        if adjustment:
            quality["rounded_rows"] += 1
            quality["rounding_delta"] = str(Decimal(quality["rounding_delta"]) + adjustment)
        quality["valid_rows"] += 1
        if parsed["value_minor"] < 0:
            quality["negative_values"] += 1
        key = (parsed["event_date"], original, parsed["category"])
        if key in seen:
            quality["duplicate_rows"] += 1
        seen.add(key)
        rows.append(parsed)
    # Compatibility names now contain exact counts, not estimates.
    quality["usable_rows_estimate"] = quality["valid_rows"]
    quality["dropped_rows_estimate"] = quality["invalid_rows"]
    return rows, quality


def load_csv(source, profile=None, progress=None):
    profile = profile or CsvProfile()
    profile.validate()
    if isinstance(source, bytes):
        raw = source
    else:
        with open(source, "rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise DataValidationError(f"Plik przekracza limit {MAX_BYTES // (1024*1024)} MiB.")
    stream = io.TextIOWrapper(io.BytesIO(raw), encoding=profile.encoding, newline="")
    blank_lines = 0
    scan_complete = True
    try:
        reader = csv.reader(stream, delimiter=profile.delimiter, strict=True)
        header = next(reader, None)
        if not header:
            p = problem(1, "Nagłówki", "", "Brak nagłówków CSV.", "Wyeksportuj tabelę z nazwami kolumn i danymi.")
            raise DataValidationError("Plik CSV jest pusty.", diagnostic_quality([p]))
        header = [name.strip() for name in header]
        if len(set(header)) != len(header) or any(not n for n in header):
            occurrences = Counter(header)
            problems = [problem(1, f"Nagłówek nr {i}", name, "Pusty lub powtórzony nagłówek.",
                                "Nadaj każdej kolumnie niepustą, unikalną nazwę.")
                        for i, name in enumerate(header, 1) if not name or occurrences[name] > 1]
            raise DataValidationError("Nagłówki muszą być niepuste i unikalne.", diagnostic_quality(problems))
        missing = [getattr(profile,k) for k in ("date_col","value_col","category_col","quantity_col","order_col","product_col","customer_col","cost_col","profit_col") if getattr(profile,k) and getattr(profile,k) not in header]
        if missing:
            problems = [problem(1, name, "", "Brak przypisanej kolumny w nagłówkach.",
                                "Wskaż właściwą kolumnę w ustawieniach albo ponów eksport z wymaganą kolumną.") for name in missing]
            raise DataValidationError("Brak kolumn: " + ", ".join(missing), diagnostic_quality(problems))
        def records():
            nonlocal blank_lines, scan_complete
            while True:
                line = reader.line_num + 1
                try:
                    row = next(reader)
                except StopIteration:
                    return
                except csv.Error:
                    scan_complete = False
                    yield (line, max(line, reader.line_num)), InvalidCsvRecord(
                        "Uszkodzona struktura CSV, np. niedomknięty cudzysłów.",
                        "Sprawdź cudzysłowy i separator albo ponów eksport CSV. Dalszych rekordów nie można bezpiecznie rozdzielić.")
                    return
                except UnicodeError:
                    scan_complete = False
                    yield None, InvalidCsvRecord("Kodowanie pliku nie pasuje do profilu.",
                        "Zmień sposób odczytania liter w ustawieniach albo ponów eksport w UTF-8. Dokładna linia jest nieznana.")
                    return
                if not row:
                    blank_lines += 1
                    continue
                if len(row) != len(header):
                    yield (line, reader.line_num), InvalidCsvRecord(
                        f"Niezgodna liczba pól: {len(row)}, oczekiwano {len(header)}.",
                        "Sprawdź brakujące lub dodatkowe separatory i cudzysłowy. Nie można bezpiecznie przypisać pól do kolumn.")
                    continue
                yield (line, reader.line_num), dict(zip(header, row))
        rows, quality = inspect_records(records(), profile, progress=progress)
    except UnicodeError as exc:
        p = problem(None, "Odczyt pliku", "", "Kodowanie pliku nie pasuje do profilu.", "Zmień sposób odczytania liter w ustawieniach albo ponów eksport w UTF-8.")
        raise DataValidationError("Kodowanie pliku nie pasuje do profilu.", diagnostic_quality([p])) from exc
    except csv.Error as exc:
        p = problem(1, "Nagłówki", "", "Niepoprawna struktura nagłówków CSV.", "Sprawdź separator i cudzysłowy albo ponów eksport CSV.")
        raise DataValidationError("Niepoprawna struktura CSV.", diagnostic_quality([p])) from exc
    finally:
        stream.close()
    quality["blank_lines"] = blank_lines
    quality["scan_complete"] = scan_complete
    if not quality["total_rows"]:
        p = problem(None, "Cały plik", "", "Plik zawiera nagłówki, ale nie zawiera rekordów.", "Wyeksportuj także dane dla wybranego okresu.")
        raise DataValidationError("Plik nie zawiera rekordów.", diagnostic_quality([p]))
    if quality["invalid_rows"]:
        details = "; ".join(f"wiersz {i['line']}: {', '.join(i['reasons'])}" for i in quality["issues"][:5])
        raise DataValidationError(f"Raport zablokowany. Błędne rekordy: {quality['invalid_rows']}. {details}", quality)
    return ParsedData(rows, quality, hashlib.sha256(raw).hexdigest())


def validate_input_dataframe(df, date_col, value_col, category_col):
    profile = CsvProfile(date_col=date_col, value_col=value_col, category_col=category_col)
    if df.empty:
        raise DataValidationError("Plik CSV jest pusty.")
    missing = [c for c in (date_col, value_col, category_col) if c not in df.columns]
    if missing:
        raise DataValidationError("Brak kolumn: " + ", ".join(missing))
    _, quality = inspect_records(enumerate(df.to_dict("records"), 2), profile)
    if quality["invalid_rows"]:
        raise DataValidationError("Niepoprawne rekordy.", quality)
