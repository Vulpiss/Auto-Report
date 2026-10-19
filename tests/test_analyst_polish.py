import unittest,io
from unittest.mock import patch
from decimal import Decimal
from app.analyst_tools import driver_page,compact_label
from app.validation import load_csv
class PolishTests(unittest.TestCase):
    def test_pagination_search_directions_and_no_mutation(self):
        rows=[dict(entity="Produkt "+str(i),current=Decimal(i),difference=Decimal(i-50)) for i in range(100)]
        shown,count,pages,page=driver_page(rows,direction="Spadki",page=3)
        self.assertEqual((count,pages,page),(50,3,3))
        self.assertEqual(len(shown),10)
        self.assertTrue(all(r["difference"]<0 for r in shown))
        self.assertEqual(driver_page(rows,query="nieistniejący")[1],0)
        self.assertEqual(rows[0]["entity"],"Produkt 0")
        self.assertEqual(len(compact_label("X"*180,40)),40)
        self.assertTrue(compact_label("X"*180,40).startswith("XXX"))
    def test_progress_counts(self):
        seen=[]
        raw=("date,value,category\n"+"2026-09-01,1,A\n"*20001).encode()
        p=load_csv(raw,progress=seen.append)
        self.assertEqual(seen,[10000,20000])
        self.assertEqual(len(p.rows),20001)
    def test_view_switch_reuses_analysis_and_same_source_import(self):
        from streamlit.testing.v1 import AppTest
        import app.analysis
        import app.validation
        with patch("app.analysis.analyze_parsed",wraps=app.analysis.analyze_parsed) as analyze,patch("app.validation.load_csv",wraps=app.validation.load_csv) as load:
            a=AppTest.from_file("interfaces/streamlit_app.py", default_timeout=20).run()
            a.checkbox(key="demo").check().run()
            a.button(key="load").click().run()
            self.assertFalse(a.exception)
            count=analyze.call_count
            a.radio(key="view").set_value("Jakość i pokrycie danych").run()
            self.assertEqual(analyze.call_count,count)
            a.button(key="load").click().run()
            self.assertEqual(load.call_count,1)
            a.text_input(key="start").set_value("2026-09-08").run()
            self.assertGreater(analyze.call_count,count)
            self.assertFalse(a.exception)

    def test_native_negative_fill_and_bounded_ticks(self):
        from app.analysis import analyze
        from app.editable_presentation import export_editable,C
        from zipfile import ZipFile
        from xml.etree import ElementTree as E
        raw=("date,value,category\n"+"2026-09-01,-10000000,A\n"*240+"2026-08-31,10000000,A\n").encode()
        from app.validation import CsvProfile
        r=analyze(raw,profile=CsvProfile(allow_negative=True),start_date="2026-09-01",end_date="2026-09-01",coverage_start="2026-08-31",coverage_end="2026-09-01")
        with ZipFile(io.BytesIO(export_editable(r))) as z:
            charts=[E.fromstring(z.read(n)) for n in z.namelist() if n.endswith(".xml") and "/charts/chart" in n]
            self.assertTrue(any("mld" in n.get("formatCode","") for c in charts for n in c.iter("{"+C+"}numFmt")))
            self.assertTrue(all(n.get("val")=="0" for c in charts for n in c.iter("{"+C+"}invertIfNegative")))
            self.assertTrue(any(float(n.get("val"))>=40 for c in charts for n in c.iter("{"+C+"}majorUnit")))

    def test_new_source_clears_coverage_and_category_selection(self):
        from streamlit.testing.v1 import AppTest
        a=AppTest.from_file("interfaces/streamlit_app.py", default_timeout=20).run()
        a.checkbox(key="demo").check().run()
        a.button(key="load").click().run()
        a.text_input(key="coverage_start").set_value("2026-09-01")
        a.text_input(key="coverage_end").set_value("2026-09-30").run()
        a.checkbox(key="all_categories").uncheck().run()
        a.checkbox(key="demo").uncheck().run()
        self.assertEqual(a.session_state["coverage_start"],"")
        self.assertEqual(a.session_state["coverage_end"],"")
        self.assertTrue(a.session_state["all_categories"])
        a.checkbox(key="demo").check().run()
        a.button(key="load").click().run()
        self.assertFalse(a.error)
        self.assertEqual(a.text_input(key="coverage_start").value,"")
        self.assertEqual(a.text_input(key="coverage_end").value,"")
