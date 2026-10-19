import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None
from app.simple_import import inspect_source, date_candidates

ROOT = Path(__file__).resolve().parents[1]

class SimpleImportTests(unittest.TestCase):
    def test_polish_csv_and_ambiguous_dates(self):
        raw = "data;kwota;kategoria\n03/04/2026;12,50;Żółć\n".encode("cp1250")
        p = inspect_source(raw)
        self.assertEqual(p["delimiter"], ";")
        self.assertTrue(p["uncertain_encoding"])
        self.assertEqual(p["rows"][0]["kategoria"], "Żółć")
        self.assertEqual(set(date_candidates(p["rows"], "data")), {"%m/%d/%Y", "%d/%m/%Y"})

    def test_utf8_and_invalid_structure(self):
        p = inspect_source("date,value,category\n2026-09-01,12,Żółć\n".encode())
        self.assertEqual(p["encoding"], "utf-8-sig")
        self.assertEqual(date_candidates(p["rows"], "date"), ["%Y-%m-%d"])
        for raw in (b"", b"date,value,category\n", b"date,value,value\n1,2,3\n"):
            with self.assertRaises(ValueError):
                inspect_source(raw)

@unittest.skipIf(AppTest is None, "Optional Streamlit is not installed.")
class SimpleAppTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix="auto-report-settings-test-")
        self.addCleanup(folder.cleanup)
        patcher = patch.dict(os.environ, {"AUTOREPORT_PROFILE_DIR": folder.name})
        patcher.start()
        self.addCleanup(patcher.stop)

    def app(self):
        return AppTest.from_file(str(ROOT / "interfaces/simple_app.py"), default_timeout=30).run()

    def test_demo_to_pdf_and_changed_period_invalidates_export(self):
        app = self.app()
        self.assertFalse(app.exception)
        app.checkbox(key="easy_demo").check().run()
        app.button(key="easy_load").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "2 250,00")
        self.assertEqual(app.metric[1].value, "14")
        self.assertFalse(app.exception)
        self.assertTrue(app.session_state["easy_pdf"].startswith(b"%PDF"))
        original = app.session_state["easy_pdf"]
        app.radio(key="easy_period").set_value("Wybieram daty").run()
        from datetime import date
        app.date_input(key="easy_start").set_value(date(2026, 9, 13)).run()
        self.assertNotEqual(app.session_state["easy_pdf"], original)
        self.assertEqual(app.session_state["easy_result"]["rows"][0]["event_date"], "2026-09-13")
        app.checkbox(key="easy_demo").uncheck().run()
        self.assertNotIn("easy_parsed", app.session_state)

    def test_ambiguous_csv_needs_date_and_meaning(self):
        raw = b"date,value,category\n03/04/2026,12,A\n"
        with patch("streamlit.file_uploader", side_effect=lambda label, **kw: io.BytesIO(raw) if kw.get("key") == "easy_upload" else None):
            app = self.app()
            self.assertFalse(app.exception)
            self.assertTrue(app.button(key="easy_load").disabled)
            app.selectbox(key="easy_config_date").set_value("%d/%m/%Y").run()
            app.selectbox(key="easy_config_meaning").set_value("amount").run()
            app.button(key="easy_load").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].value, "12,00")
            self.assertEqual(app.session_state["easy_result"]["rows"][0]["event_date"], "2026-04-03")

    def test_invalid_source_clears_old_report(self):
        current = [b"date,value,category\n2026-09-01,12,A\n"]
        with patch("streamlit.file_uploader", side_effect=lambda label, **kw: io.BytesIO(current[0]) if kw.get("key") == "easy_upload" else None):
            app = self.app()
            app.selectbox(key="easy_config_meaning").set_value("amount").run()
            app.button(key="easy_load").click().run()
            self.assertTrue(app.session_state["easy_pdf"].startswith(b"%PDF"))
            current[0] = b"date,value,category\n2026-09-01,broken,A\n"
            app.run()
            self.assertNotIn("easy_pdf", app.session_state)
            app.selectbox(key="easy_config_meaning").set_value("amount").run()
            app.button(key="easy_load").click().run()
            self.assertFalse(app.exception)
            self.assertTrue(app.error)
            self.assertNotIn("easy_parsed", app.session_state)

    def test_advanced_mode_available(self):
        app = self.app()
        app.radio(key="ui_mode").set_value("Zaawansowany").run()
        self.assertFalse(app.exception)
        app.checkbox(key="demo").check().run()
        app.button(key="load").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "1 250,00")

    def test_saved_business_profile_preserves_extra_columns(self):
        import json
        from test_business_upgrade import CSV, PROFILE
        saved = json.dumps(PROFILE.to_dict()).encode()
        with patch("streamlit.file_uploader", side_effect=lambda label, **kw: io.BytesIO(CSV if kw.get("key") == "easy_upload" else saved)):
            app = self.app()
            app.button(key="easy_restore").click().run()
            app.button(key="easy_load").click().run()
            self.assertFalse(app.exception)
            app.radio(key="easy_period").set_value("Ostatnie 7 dni w pliku").run()
            self.assertEqual(app.metric[0].value, "600,00")
            self.assertEqual(app.selectbox(key="easy_config_currency").value, PROFILE.currency)
            self.assertEqual(app.selectbox(key="easy_config_basis").value, PROFILE.amount_basis)
            self.assertTrue(any(m.value == "230,00" for m in app.metric))

    def test_unit_price_requires_quantity_and_retains_exact_sum(self):
        raw = b"date,value,category,Quantity\n2026-09-01,12.50,A,3\n2026-09-02,1.25,B,2\n"
        with patch("streamlit.file_uploader", side_effect=lambda label, **kw: io.BytesIO(raw) if kw.get("key") == "easy_upload" else None):
            app = self.app()
            app.selectbox(key="easy_config_meaning").set_value("unit_price").run()
            app.button(key="easy_load").click().run()
            self.assertTrue(app.error)
            app.selectbox(key="easy_config_quantity").set_value("Quantity").run()
            app.text_input(key="easy_config_unit").set_value("szt.").run()
            app.button(key="easy_load").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].value, "40,00")

    def test_second_file_in_new_session_only_needs_one_button(self):
        current = [b"date,value,category\n2026-09-01,12,A\n"]
        with patch("streamlit.file_uploader", side_effect=lambda label, **kw: io.BytesIO(current[0]) if kw.get("key") == "easy_upload" else None):
            first = self.app()
            first.selectbox(key="easy_config_meaning").set_value("amount").run()
            first.selectbox(key="easy_config_currency").set_value("EUR").run()
            first.button(key="easy_load").click().run()
            self.assertFalse(first.exception)
            current[0] = b"date,value,category\n2026-10-01,15,A\n2026-10-03,25,B\n"
            second = self.app()
            self.assertFalse(second.button(key="easy_load").disabled)
            self.assertEqual(second.selectbox(key="easy_config_currency").value, "EUR")
            second.button(key="easy_load").click().run()
            self.assertFalse(second.exception)
            self.assertEqual(second.metric[0].value, "40,00")
            self.assertEqual(second.metric[1].value, "2")
            self.assertTrue(second.session_state["easy_pdf"].startswith(b"%PDF"))

    def test_pdf_failure_keeps_screen_report_and_allows_retry(self):
        app = self.app()
        app.checkbox(key="easy_demo").check().run()
        with patch("app.pipeline.export_analysis", side_effect=OSError("Brak miejsca")):
            app.button(key="easy_load").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, "2 250,00")
        self.assertNotIn("easy_pdf", app.session_state)
        app.button(key="easy_export").click().run()
        self.assertFalse(app.exception)
        self.assertTrue(app.session_state["easy_pdf"].startswith(b"%PDF"))

    def test_remembered_windows_encoding_handles_next_ascii_only_file(self):
        from app.profile_library import remember
        from app.validation import CsvProfile
        remember(["date", "value", "category"], CsvProfile(encoding="cp1250", currency="EUR"))
        raw = b"date,value,category\n2026-10-01,42,A\n"
        with patch("streamlit.file_uploader", side_effect=lambda label, **kw: io.BytesIO(raw) if kw.get("key") == "easy_upload" else None):
            app = self.app()
            self.assertFalse(app.button(key="easy_load").disabled)
            self.assertEqual(app.selectbox(key="easy_config_encoding").value, "cp1250")
            app.button(key="easy_load").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].value, "42,00")

    def test_multiple_saved_encodings_do_not_choose_currency_silently(self):
        from app.profile_library import remember
        from app.validation import CsvProfile
        for encoding, currency in [("cp1250", "PLN"), ("utf-8-sig", "EUR")]:
            remember(["date", "value", "category"], CsvProfile(encoding=encoding, currency=currency))
        raw = b"date,value,category\n2026-10-01,42,A\n"
        with patch("streamlit.file_uploader", side_effect=lambda label, **kw: io.BytesIO(raw) if kw.get("key") == "easy_upload" else None):
            app = self.app()
            self.assertFalse(app.exception)
            self.assertTrue(app.button(key="easy_load").disabled)
            self.assertTrue(any("kilka zapisanych" in item.value for item in app.caption))
