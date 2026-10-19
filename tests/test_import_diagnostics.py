import csv
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app.analysis import analyze
from app.import_diagnostics import diagnostic_rows, diagnostics_csv
from app.simple_import import inspect_source
from app.validation import CsvProfile, DataValidationError, load_csv

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None

ROOT = Path(__file__).resolve().parents[1]


class ImportDiagnosticsTests(unittest.TestCase):
    def failure(self, raw, profile=None):
        with self.assertRaises(DataValidationError) as caught:
            load_csv(raw, profile)
        return caught.exception.quality

    def test_all_fields_and_exact_counts_without_losing_good_rows(self):
        q = self.failure(b"date,value,category\n2026-10-01,10,A\n,abc,A\n2026-10-02,20,B\n2026-10-02,30,\n")
        rows = diagnostic_rows(q)
        self.assertEqual((q["total_rows"], q["valid_rows"], q["invalid_rows"]), (4, 2, 2))
        self.assertEqual([(r["Linia CSV"], r["Kolumna"], r["Wartość (podgląd)"]) for r in rows],
                         [("3", "date", ""), ("3", "value", "abc"), ("5", "category", "")])
        self.assertTrue(all(r["Co poprawić"] for r in rows))
        self.assertIn("2026-10-02", rows[0]["Co poprawić"])
        self.assertTrue(q["scan_complete"])

    def test_more_than_fifty_bad_rows_export_and_page_have_every_location(self):
        raw = ("date,value,category\n" + "2026-10-01,abc,\n" * 75).encode()
        q = self.failure(raw)
        self.assertEqual(q["invalid_rows"], 75)
        self.assertEqual(len(q["issues"]), 75)
        exported = list(csv.DictReader(io.StringIO(diagnostics_csv(q).decode("utf-8-sig")), delimiter=";"))
        self.assertEqual(len(exported), 150)
        self.assertEqual(exported[-1]["Linia CSV"], "76")
        self.assertEqual(exported[-1]["Kolumna"], "category")
        self.assertEqual(diagnostic_rows(q, 100, 100), exported[100:])

    def test_multiline_fields_and_blank_lines_have_physical_locations(self):
        q = self.failure(b'date,value,category\n2026-10-01,10,"A\nB"\n\n2026-10-02,abc,A\n')
        self.assertEqual([r["Linia CSV"] for r in diagnostic_rows(q)], ["2–3", "5"])
        self.assertEqual(q["blank_lines"], 1)

    def test_ragged_rows_and_value_errors_are_all_reported(self):
        q = self.failure(b"date,value,category\n2026-10-01,10\n2026-10-02,abc,A\n2026-10-03,30,A,extra\n")
        rows = diagnostic_rows(q)
        self.assertEqual([(r["Linia CSV"], r["Kolumna"]) for r in rows],
                         [("2", "Cały wiersz"), ("3", "value"), ("4", "Cały wiersz")])
        self.assertEqual(q["invalid_rows"], 3)
        self.assertTrue(q["scan_complete"])

    def test_broken_quotes_preserve_prior_errors_and_mark_unchecked_tail(self):
        q = self.failure(b'date,value,category\n2026-10-01,abc,A\n2026-10-02,10,"unfinished\n2026-10-03,20,A\n')
        self.assertFalse(q["scan_complete"])
        self.assertEqual([r["Linia CSV"] for r in diagnostic_rows(q)], ["2", "3–4"])

    def test_missing_and_duplicate_headers_have_locations(self):
        q = self.failure(b"date,value\n2026-10-01,10\n")
        self.assertEqual([(r["Linia CSV"], r["Kolumna"]) for r in diagnostic_rows(q)], [("1", "category")])
        q = self.failure(b"date,value,value\n2026-10-01,10,20\n")
        self.assertEqual([r["Kolumna"] for r in diagnostic_rows(q)], ["Nagłówek nr 2", "Nagłówek nr 3"])

    def test_optional_blanks_are_located_and_metrics_stay_unavailable(self):
        raw = b"date,value,category,qty,cost,doc\n2026-10-01,100,A,,,N1\n2026-10-02,200,A,2,120,N2\n"
        profile = CsvProfile(quantity_col="qty", cost_col="cost", order_col="doc", quantity_unit="szt.", value_is_sales=True)
        result = analyze(raw, profile=profile, start_date="2026-10-01", end_date="2026-10-02")
        rows = diagnostic_rows(result["quality"])
        self.assertEqual([(r["Typ"], r["Linia CSV"], r["Kolumna"]) for r in rows],
                         [("Ostrzeżenie", "2", "qty"), ("Ostrzeżenie", "2", "cost")])
        self.assertEqual(result["kpis"]["total_minor"], 30000)
        self.assertEqual(result["business"]["orders"], 2)
        for key in ("quantity", "cost", "profit", "margin_pct"):
            self.assertIsNone(result["business"][key])

    def test_all_invalid_optional_fields_are_located_in_same_record(self):
        profile = CsvProfile(quantity_col="qty", cost_col="cost", quantity_unit="szt.")
        q = self.failure(b"date,value,category,qty,cost\n2026-10-01,100,A,abc,NaN\n", profile)
        self.assertEqual({r["Kolumna"] for r in diagnostic_rows(q)}, {"qty", "cost"})
        self.assertEqual(q["invalid_rows"], 1)

    def test_optional_blanks_are_reported_even_when_same_row_has_blocking_error(self):
        profile = CsvProfile(cost_col="cost")
        q = self.failure(b"date,value,category,cost\n2026-10-01,abc,A,\n", profile)
        self.assertEqual([(r["Typ"], r["Kolumna"]) for r in diagnostic_rows(q)],
                         [("Błąd", "value"), ("Ostrzeżenie", "cost")])

    def test_price_times_quantity_does_not_invent_second_error(self):
        profile = CsvProfile(value_mode="unit_price", quantity_col="qty", quantity_unit="szt.", cost_col="cost")
        q = self.failure(b"date,value,category,qty,cost\n2026-10-01,10,A,2,abc\n", profile)
        self.assertEqual([r["Kolumna"] for r in diagnostic_rows(q)], ["cost"])
        q = self.failure(b"date,value,category,qty,cost\n2026-10-01,10,A,,20\n", profile)
        self.assertEqual([r["Kolumna"] for r in diagnostic_rows(q)], ["qty"])
        self.assertIn("cena × ilość", diagnostic_rows(q)[0]["Problem"])

    def test_export_quotes_special_characters_and_prevents_formula_execution(self):
        q = self.failure('date,value,category\n2026-10-01,"=1;2",Żółć\n'.encode())
        raw = diagnostics_csv(q)
        self.assertTrue(raw.startswith(b"\xef\xbb\xbf"))
        row = next(csv.DictReader(io.StringIO(raw.decode("utf-8-sig")), delimiter=";"))
        self.assertEqual(row["Wartość (podgląd)"], "'=1;2")

    def test_preview_structure_error_points_to_bad_line(self):
        with self.assertRaises(DataValidationError) as caught:
            inspect_source(b"date,value,category\n2026-10-01,10,A\n2026-10-02,20\n")
        row = diagnostic_rows(caught.exception.quality)[0]
        self.assertEqual(row["Linia CSV"], "3")
        self.assertEqual(row["Kolumna"], "Cały wiersz")


@unittest.skipIf(AppTest is None, "Optional Streamlit is not installed.")
class ImportFeedbackTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix="auto-report-diagnostics-test-")
        self.addCleanup(folder.cleanup)
        env = patch.dict(os.environ, {"AUTOREPORT_PROFILE_DIR": folder.name})
        env.start()
        self.addCleanup(env.stop)

    def app(self, name):
        return AppTest.from_file(str(ROOT / "interfaces" / name), default_timeout=30).run()

    def repair_table(self, app):
        return next(table.value for table in app.dataframe if "Co poprawić" in table.value.columns)

    def test_simple_list_survives_reruns_and_disappears_after_corrected_import(self):
        current = [b"date,value,category\n2026-10-01,10,A\n2026-10-02,abc,A\n2026-10-03,30,\n"]
        with patch("streamlit.file_uploader", side_effect=lambda label, **kw: io.BytesIO(current[0]) if kw.get("key") == "easy_upload" else None):
            app = self.app("simple_app.py")
            app.selectbox(key="easy_config_meaning").set_value("amount").run()
            app.button(key="easy_load").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(list(self.repair_table(app)["Linia CSV"]), ["3", "4"])
            self.assertNotIn("easy_pdf", app.session_state)
            app.run()
            self.assertEqual(len(self.repair_table(app)), 2)
            current[0] = b"date,value,category\n2026-10-01,10,A\n2026-10-02,20,A\n2026-10-03,30,B\n"
            app.run()
            app.selectbox(key="easy_config_meaning").set_value("amount").run()
            app.button(key="easy_load").click().run()
            self.assertFalse(app.exception)
            self.assertNotIn("easy_import_error", app.session_state)
            self.assertFalse(any("Co poprawić" in table.value.columns for table in app.dataframe))
            self.assertEqual(app.metric[0].value, "60,00")

    def test_simple_bad_preview_has_repair_list(self):
        raw = b"date,value,category\n2026-10-01,10,A\n2026-10-02,20\n"
        with patch("streamlit.file_uploader", side_effect=lambda label, **kw: io.BytesIO(raw) if kw.get("key") == "easy_upload" else None):
            app = self.app("simple_app.py")
            self.assertFalse(app.exception)
            self.assertEqual(list(self.repair_table(app)["Linia CSV"]), ["3"])

    def test_advanced_pagination_keeps_error_list_and_settings_change_clears_it(self):
        raw = ("date,value,category\n" + "2026-10-01,abc,\n" * 75).encode()
        with patch("streamlit.file_uploader", side_effect=lambda label, **kw: io.BytesIO(raw) if label == "Eksport CSV" else None):
            app = self.app("streamlit_app.py")
            app.button(key="load").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(len(self.repair_table(app)), 100)
            app.number_input(key="advanced_problems_page").set_value(2).run()
            self.assertFalse(app.exception)
            self.assertEqual(len(self.repair_table(app)), 50)
            self.assertEqual(self.repair_table(app).iloc[-1]["Linia CSV"], "76")
            self.assertNotIn("pdf", app.session_state)
            app.selectbox(key="decimal_separator").set_value(",").run()
            self.assertNotIn("import_error", app.session_state)

    def test_advanced_optional_blanks_show_warning_locations(self):
        raw = b"date,value,category,cost\n2026-10-01,100,A,\n"
        with patch("streamlit.file_uploader", side_effect=lambda label, **kw: io.BytesIO(raw) if label == "Eksport CSV" else None):
            app = self.app("streamlit_app.py")
            app.selectbox(key="cost_col").set_value("cost").run()
            app.button(key="load").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(list(self.repair_table(app)["Typ"]), ["Ostrzeżenie"])
            self.assertEqual(list(self.repair_table(app)["Kolumna"]), ["cost"])


if __name__ == "__main__":
    unittest.main()
