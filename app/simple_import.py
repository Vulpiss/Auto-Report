"""Conservative suggestions for the guided importer; full validation stays shared."""
import csv
import io
from app.validation import DATE_FORMATS, MAX_BYTES, parse_date, DataValidationError
from app.import_diagnostics import problem, diagnostic_quality
from app.workspace import propose

DATE_LABELS = {
    "%Y-%m-%d": "2026-09-28 — rok, miesiąc, dzień",
    "%d.%m.%Y": "28.09.2026 — dzień, miesiąc, rok",
    "%m/%d/%Y": "09/28/2026 — miesiąc / dzień / rok",
    "%d/%m/%Y": "28/09/2026 — dzień / miesiąc / rok",
    "%m/%d/%Y %H:%M": "09/28/2026 14:30 — miesiąc / dzień / rok i godzina",
    "%d/%m/%Y %H:%M": "28/09/2026 14:30 — dzień / miesiąc / rok i godzina",
    "%Y-%m-%d %H:%M:%S": "2026-09-28 14:30:00 — rok, miesiąc, dzień i godzina",
}

def inspect_source(raw, encoding=None, delimiter=None):
    if not raw:
        raise ValueError("Ten plik jest pusty. Wybierz eksport zawierający dane.")
    if len(raw) > MAX_BYTES:
        raise ValueError("Plik przekracza 100 MiB. Wyeksportuj krótszy okres.")
    # A bounded byte sample, decoded incrementally to avoid a split UTF-8 character.
    import codecs
    sample = raw[:65536]
    uncertain_encoding = False
    if encoding is None:
        try:
            codecs.getincrementaldecoder("utf-8-sig")().decode(sample, final=False)
            encoding = "utf-8-sig"
        except UnicodeError:
            encoding = "cp1250"
            uncertain_encoding = True
    text = codecs.getincrementaldecoder(encoding)().decode(sample, final=False)
    if len(raw) > len(sample):
        text = text.rsplit("\n", 1)[0]
    if delimiter is None:
        try:
            delimiter = csv.Sniffer().sniff(text, delimiters=",;\t").delimiter
        except csv.Error:
            try:
                delimiter = csv.Sniffer().sniff(text.splitlines()[0], delimiters=",;\t").delimiter
            except csv.Error:
                p = problem(None, "Odczyt pliku", "", "Nie rozpoznano podziału na kolumny.",
                            "Otwórz „Popraw odczyt pliku” i wybierz separator CSV.")
                raise DataValidationError(p["problem"], diagnostic_quality([p]))
    reader = csv.reader(io.StringIO(text), delimiter=delimiter, strict=True)
    line = 1
    try:
        headers = [v.strip() for v in next(reader, [])]
        if len(headers) < 3 or any(not h for h in headers) or len(set(headers)) != len(headers):
            p = problem(1, "Nagłówki", ", ".join(headers), "Potrzebne są co najmniej trzy kolumny z niepustymi, różnymi nazwami.",
                        "Sprawdź pierwszy wiersz i separator. Wymagane są kolumny daty, kwoty i kategorii.")
            raise DataValidationError(p["problem"], diagnostic_quality([p]))
        rows = []
        while True:
            line = reader.line_num + 1
            row = next(reader, None)
            if row is None:
                break
            if not row:
                continue
            if len(row) != len(headers):
                p = problem(line, "Cały wiersz", "", f"Niezgodna liczba pól: {len(row)}, oczekiwano {len(headers)}.",
                            "Sprawdź separatory i cudzysłowy albo zmień sposób odczytu pliku.", line_end=reader.line_num)
                raise DataValidationError(p["problem"], diagnostic_quality([p]))
            rows.append(dict(zip(headers, row)))
            if len(rows) >= 100:
                break
    except csv.Error as exc:
        p = problem(line, "Cały wiersz", "", "Plik ma uszkodzoną strukturę CSV.",
                    "Sprawdź cudzysłowy i separator albo ponów eksport CSV.", line_end=reader.line_num)
        raise DataValidationError(p["problem"], diagnostic_quality([p])) from exc
    if not rows:
        raise ValueError("Plik zawiera tylko nazwy kolumn. Wyeksportuj także dane.")
    return dict(headers=headers, rows=rows, mapping=propose(headers), encoding=encoding,
                delimiter=delimiter, uncertain_encoding=uncertain_encoding)

def date_candidates(rows, column):
    values = [r[column].strip() for r in rows if r.get(column, "").strip()]
    candidates = []
    for fmt in DATE_FORMATS:
        try:
            if values:
                for value in values:
                    parse_date(value, fmt)
                candidates.append(fmt)
        except ValueError:
            pass
    return candidates

def error_help(exc):
    text = str(exc)
    if "kwot" in text.lower() or "value:" in text:
        return "Sprawdź wskazane kwoty: puste pola, zapis z przecinkiem lub kropką oraz wartości ujemne. Program nie zastępuje błędnych kwot zerami."
    if "dat" in text.lower():
        return "Sprawdź wskazaną datę i kolejność dnia oraz miesiąca. Popraw plik lub wybierz pasujący przykład daty."
    return "Wróć do ustawień pliku poniżej albo popraw wskazany wiersz w programie źródłowym i ponownie wybierz CSV."
