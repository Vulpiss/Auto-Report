"""Locations and repair instructions for CSV problems; source files stay untouched."""
import csv
import io
from itertools import islice

VALUE_PREVIEW_LIMIT = 200
TABLE_COLUMNS = ("Typ", "Linia CSV", "Kolumna", "Wartość (podgląd)", "Problem", "Co poprawić")


def problem(line, column, value, message, hint, *, warning=False, line_end=None):
    text = "" if value is None else str(value)
    if len(text) > VALUE_PREVIEW_LIMIT:
        text = text[:VALUE_PREVIEW_LIMIT] + "… [skrócono]"
    return dict(line=line, line_end=line_end or line, column=column, value=text,
                problem=message, hint=hint, warning=warning)


def diagnostic_quality(problems, *, scan_complete=False):
    return dict(total_rows=0, valid_rows=0, invalid_rows=0, scan_complete=scan_complete,
                issues=[dict(line=p["line"], reasons=[p["problem"]], problems=[p]) for p in problems])


def iter_problems(quality):
    for group in ("issues", "warnings"):
        for issue in quality.get(group, []):
            yield from issue.get("problems", [])


def diagnostic_rows(quality, limit=None, offset=0):
    result = []
    for item in islice(iter_problems(quality), offset, None if limit is None else offset + limit):
        line = item["line"]
        end = item.get("line_end", line)
        location = "Cały plik" if line is None else str(line) if end == line else f"{line}–{end}"
        result.append(dict(zip(TABLE_COLUMNS, (
            "Ostrzeżenie" if item.get("warning") else "Błąd", location, item["column"],
            item["value"], item["problem"], item["hint"]))))
    return result


def diagnostics_csv(quality):
    """Excel-compatible UTF-8 CSV; values are text, never spreadsheet formulas."""
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter=";")
    writer.writerow(TABLE_COLUMNS)
    for item in iter_problems(quality):
        line, end = item["line"], item.get("line_end", item["line"])
        location = "Cały plik" if line is None else str(line) if end == line else f"{line}–{end}"
        cells = ["Ostrzeżenie" if item.get("warning") else "Błąd", location,
                 item["column"], item["value"], item["problem"], item["hint"]]
        writer.writerow(["'" + cell if cell.lstrip().startswith(("=", "+", "-", "@")) else cell
                         for cell in cells])
    return stream.getvalue().encode("utf-8-sig")
