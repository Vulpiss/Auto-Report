"""Small synthetic fixtures with expectations independent of app calculations."""
import csv
from datetime import date, timedelta
import io
from app.validation import CsvProfile


def encode(headers, rows):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def cases():
    origin = date(2026, 9, 23)
    cents = [1] * 7 + [1, 2, -1, 0, 1, -2, 3]
    tiny = encode(["date", "value", "category"],
                  [(origin + timedelta(days=i), f"{v/100:.2f}", "Papier") for i, v in enumerate(cents)])
    yield dict(name="grosze-i-zwroty", raw=tiny, profile=CsvProfile(allow_negative=True),
               options=dict(start_date="2026-09-30", end_date="2026-10-06", coverage_start="2026-09-23", coverage_end="2026-10-06"),
               expected=dict(total_minor=4, rows=7, average="0.01", previous_minor=7),
               pdf_tokens=["0,04", "0,01", "0,07"])
    long = encode(["date", "value", "category"],
                  [(f"2026-10-{1+i%6:02}", str(i+1), f"K{i+1:02} " + "Żółć wyposażenie biurowe " * 7) for i in range(36)])
    yield dict(name="dlugie-kategorie", raw=long, profile=CsvProfile(),
               options=dict(start_date="2026-10-01", end_date="2026-10-06"),
               expected=dict(total_minor=66600, rows=36, average="18.50"),
               pdf_tokens=["666,00", "18,50", "351,00", "K36", "K27"])
    business = encode(["date", "value", "category", "quantity", "order", "cost"],
                      [(date(2026, 9, 25) + timedelta(days=i), "100", ["Papier", "Teczki", "Środki czystości"][i%3], "1", f"D{i//2}", "60") for i in range(12)])
    yield dict(name="rentownosc-i-kontrola", raw=business,
               profile=CsvProfile(quantity_col="quantity", quantity_unit="szt.", order_col="order", cost_col="cost", value_is_sales=True, amount_basis="netto"),
               options=dict(start_date="2026-10-01", end_date="2026-10-06", coverage_start="2026-09-25", coverage_end="2026-10-06", title="Raport demonstracyjny wartości pozycji, dokumentów i rentowności z kontrolą kompletności eksportu oraz jawnymi regułami interpretacji"),
               expected=dict(total_minor=60000, rows=6, average="100.00", previous_minor=60000,
                             business=dict(orders=3, quantity="6", cost="360", profit="240", average_order="200", margin_pct="40")),
               pdf_tokens=["600,00", "100,00", "360,00", "240,00", "40,00", "Dokumenty i rentowność"])
