import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest=None
ROOT=Path(__file__).resolve().parents[1]

@unittest.skipIf(AppTest is None,"Optional Streamlit is not installed.")
class StreamlitTests(unittest.TestCase):
    def app(self):
        return AppTest.from_file(str(ROOT/"interfaces/streamlit_app.py"),default_timeout=20).run()
    def test_missing_upload_is_visible_error(self):
        app=self.app()
        app.button(key="load").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.error),1)
    def test_uploaded_bytes_and_chosen_dates_reach_pipeline(self):
        data=b"date,value,category\n2026-09-01,12,A\n2026-09-02,34,B\n"
        with tempfile.TemporaryDirectory() as d, patch("streamlit.file_uploader",return_value=io.BytesIO(data)),patch("app.pipeline.OUTPUT_DIR",d):
            app=self.app()
            app.button(key="load").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(list(Path(d).iterdir()),[]) # Analysis does not write PDF.
            app.text_input(key="start").set_value("2026-09-02")
            app.text_input(key="end").set_value("2026-09-02").run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].value,"34,00")
            app.button(key="export").click().run()
            self.assertFalse(app.exception)
            summary=json.loads(next(Path(d).glob("*/summary.json")).read_text())
            self.assertEqual(summary["kpis"]["total_minor"],3400)
            self.assertEqual(summary["kpis"]["rows_cnt"],1)
            self.assertIn("pdf",app.session_state)
            app.text_input(key="start").set_value("2026-09-01").run()
            self.assertNotIn("pdf",app.session_state)
    def test_empty_categories_and_invalid_dates_clear_export(self):
        app=self.app()
        app.checkbox(key="demo").check().run()
        app.button(key="load").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.radio(key="view").options),3)
        app.checkbox(key="all_categories").uncheck().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric),0)
        self.assertTrue(any("Brak pozycji" in x.value for x in app.info))
        app.checkbox(key="all_categories").check().run()
        app.text_input(key="start").set_value("wrong").run()
        self.assertEqual(len(app.error),1)
        self.assertEqual(len(app.metric),0)
    def test_source_change_invalidates_results(self):
        app=self.app()
        app.checkbox(key="demo").check().run()
        app.button(key="load").click().run()
        self.assertEqual(len(app.metric),3)
        app.checkbox(key="demo").uncheck().run()
        self.assertEqual(len(app.metric),0)
        self.assertNotIn("parsed",app.session_state)

    def test_category_focus_updates_global_scope(self):
        app=self.app()
        app.checkbox(key="demo").check().run()
        app.button(key="load").click().run()
        app.selectbox(key="focus").set_value("Papier").run()
        app.button(key="focus_apply").click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.checkbox(key="all_categories").value)
        self.assertEqual(app.multiselect(key="categories").value,["Papier"])
        self.assertEqual(app.metric[0].value,"550,00")
        self.assertEqual(app.metric[1].value,"3")

    def test_view_switch_preserves_scope_and_pptx_invalidation(self):
        app=self.app()
        app.checkbox(key="demo").check().run()
        app.button(key="load").click().run()
        app.radio(key="view").set_value("Kategorie i źródła zmiany").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.text_input(key="start").value,"2026-09-07")
        app.selectbox(key="pptx_scope").set_value("Bieżący dashboard").run()
        app.button(key="export_pptx").click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertTrue(app.session_state["pptx"].startswith(b"PK"))
        app.radio(key="view").set_value("Jakość i pokrycie danych").run()
        self.assertFalse(app.exception)
        self.assertNotIn("pptx",app.session_state)

    def test_category_table_pages_and_filter_reset(self):
        data=("date,value,category\n"+"".join(f"2026-09-02,{i+1},C{i:03}\n" for i in range(205))).encode()
        with patch("streamlit.file_uploader",return_value=io.BytesIO(data)):
            app=self.app()
            app.button(key="load").click().run()
            app.number_input(key="category_page_0").set_value(3).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].value,"21 115,00")
            app.selectbox(key="focus").set_value("C000").run()
            app.button(key="focus_apply").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.number_input(key="category_page_0").value,1)
            self.assertEqual(app.metric[0].value,"1,00")

    def test_external_preset_requires_explicit_rounding(self):
        raw="Order Date,Sales,Sub-Category\n1/13/2017,1.235,Café\n".encode("cp1252")
        with patch("streamlit.file_uploader",return_value=io.BytesIO(raw)):
            app=self.app()
            app.button(key="superstore_profile").click().run()
            app.button(key="load").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.error),1)
            app.selectbox(key="precision").set_value("half_up").run()
            app.button(key="load").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].value,"1,24")
            self.assertIn("j.p.",app.metric[0].label)
            self.assertTrue(any("HALF_UP" in x.value for x in app.warning))
            app.selectbox(key="currency").set_value("USD").run()
            self.assertNotIn("parsed",app.session_state)

    def test_business_mapping_and_global_product_filter(self):
        from test_business_upgrade import CSV
        with patch("streamlit.file_uploader",side_effect=lambda label,**kw:io.BytesIO(CSV) if label=="Eksport CSV" else None):
            app=self.app()
            app.button(key="accept_mapping").click().run()
            app.text_input(key="quantity_unit").set_value("szt.")
            app.checkbox(key="value_is_sales").check().run()
            app.button(key="load").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.metric[0].value,"600,00")
            self.assertTrue(any(x.value=="230,00" for x in app.metric))
            app.multiselect(key="product_filter").set_value(["P1"]).run()
            self.assertEqual(app.metric[0].value,"500,00")
            self.assertTrue(any(x.value=="210,00" for x in app.metric))
            app.selectbox(key="grouping").set_value("Miesiąc").run()
            self.assertFalse(app.exception)

    def test_session_restore_and_wrong_source_block(self):
        from test_business_upgrade import CSV,PROFILE
        from app.workspace import encode_session
        state={"start":"2026-09-01","end":"2026-09-03","comparison_mode":"Rok do roku",
               "coverage_start":"2025-09-01","coverage_end":"2026-09-30","grouping":"Miesiąc",
               "pptx_title":"Zapisany tytuł","pptx_comment":"Komentarz","view":"Kategorie i źródła zmiany","product_filter":["P1"]}
        saved=encode_session(CSV,PROFILE,state)
        with patch("streamlit.file_uploader",side_effect=lambda label,**kw:io.BytesIO(CSV if label=="Eksport CSV" else saved)):
            app=self.app()
            app.button(key="restore_settings").click().run()
            app.run()  # Settings must survive another rerun before import.
            app.button(key="load").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.radio(key="view").value,"Kategorie i źródła zmiany")
            self.assertEqual(app.text_input(key="start").value,state["start"])
            self.assertEqual(app.selectbox(key="comparison_mode").value,"Rok do roku")
            self.assertEqual(app.text_area(key="pptx_comment").value,"Komentarz")
            self.assertEqual(app.multiselect(key="product_filter").value,["P1"])
            self.assertEqual(app.text_input(key="coverage_start").value,state["coverage_start"])
            self.assertEqual(app.text_input(key="coverage_end").value,state["coverage_end"])
            self.assertIsNotNone(app.session_state["analysis_result"]["comparison"]["difference"]["total_value"])
        with patch("streamlit.file_uploader",side_effect=lambda label,**kw:io.BytesIO(CSV+b"\n" if label=="Eksport CSV" else saved)):
            app=self.app();app.button(key="restore_settings").click().run()
            self.assertFalse(app.exception)
            self.assertTrue(any("innego CSV" in x.value for x in app.error))

    def test_pending_session_is_discarded_when_source_changes_before_import(self):
        from test_business_upgrade import CSV,PROFILE
        from app.workspace import encode_session
        current=[CSV]
        saved=encode_session(CSV,PROFILE,{"start":"2026-09-01","end":"2026-09-03",
            "coverage_start":"2025-09-01","coverage_end":"2026-09-30"})
        with patch("streamlit.file_uploader",side_effect=lambda label,**kw:io.BytesIO(current[0] if label=="Eksport CSV" else saved)):
            app=self.app()
            app.button(key="restore_settings").click().run()
            self.assertIn("pending_settings",app.session_state)
            current[0]=CSV+b"\n"
            app.run()
            self.assertNotIn("pending_settings",app.session_state)
            app.button(key="load").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.text_input(key="coverage_start").value,"")
            self.assertEqual(app.text_input(key="coverage_end").value,"")
