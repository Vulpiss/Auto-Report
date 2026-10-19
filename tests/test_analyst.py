"""Independent contracts for interactive models and portable PPTX exports."""
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from decimal import Decimal
from app.analysis import analyze
from app.validation import CsvProfile
from app.dashboard_model import make_model
from app.presentation import export_pptx,A,P
ROOT=Path(__file__).resolve().parents[1]
class AnalystTests(unittest.TestCase):
    def sample(self,**kwargs):
        return analyze(ROOT/"sample_data/dashboard_reference.csv",profile=CsvProfile(allow_negative=True,amount_basis="netto"),
                       start_date="2026-09-03",end_date="2026-09-04",coverage_start="2026-09-01",coverage_end="2026-09-04",**kwargs)
    def test_daily_alignment_and_signed_structure(self):
        r=self.sample();m=make_model(r)
        self.assertEqual([t["current"] for t in m["trend"]],[130,250])
        self.assertEqual([t["previous"] for t in m["trend"]],[150,200])
        self.assertEqual(sum(x["value"] for x in m["structure"]),380)
        self.assertEqual(sum(x["value"] for x in m["structure"] if x["sign"]=="Ujemne"),-20)
        self.assertEqual(sum(x["value"] for x in m["changes"]),30)
    def test_weekly_aggregates_preserve_scope(self):
        m=make_model(self.sample(categories=["A"]),"Tydzień")
        self.assertEqual(len(m["trend"]),1)
        self.assertEqual((m["trend"][0]["current"],m["trend"][0]["previous"]),(400,300))
        self.assertEqual(sum(x["value"] for x in m["structure"]),400)
        self.assertEqual(m["trend"][0]["state"],"Częściowy tydzień")
    def test_gaps_not_zero_and_previous_unavailable(self):
        r=analyze(b"date,value,category\n2026-09-01,10,A\n2026-09-03,20,A\n",start_date="2026-09-01",end_date="2026-09-03")
        m=make_model(r)
        self.assertIsNone(m["trend"][1]["current"])
        self.assertTrue(all(t["previous"] is None for t in m["trend"]))
        self.assertIsNone(make_model(r,"Tydzień")["trend"][0]["current"])
    def inspect(self,data,count):
        z=zipfile.ZipFile(BytesIO(data))
        self.assertIsNone(z.testzip())
        slides=[n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
        self.assertEqual(len(slides),count)
        root=ET.fromstring(z.read("ppt/presentation.xml"))
        self.assertEqual(len(root.find("{"+P+"}sldIdLst")),count)
        for name in slides:
            self.assertNotIn(b"{{",z.read(name))
        return z
    def test_three_slides_have_actual_filters_and_money(self):
        r=self.sample(categories=["A"])
        z=self.inspect(export_pptx(r,title="Próba & <kwoty>",comment="Zażółć gęślą jaźń"),3)
        notes=[n for n in z.namelist() if n.startswith("ppt/notesSlides/notesSlide") and n.endswith(".xml")]
        self.assertEqual(len(notes),3)
        for name in notes:
            text="".join(n.text or "" for n in ET.fromstring(z.read(name)).iter("{"+A+"}t"))
            self.assertIn('"total_minor": 40000',text)
            self.assertIn('"selected_categories": ["A"]',text)
            self.assertIn(r["source_sha256"],text)
            self.assertIn("Zażółć",text)
        self.assertEqual(len([n for n in z.namelist() if n.startswith("ppt/media/")]),3)
    def test_single_quality_slide_removes_other_content(self):
        z=self.inspect(export_pptx(self.sample(),(2,),grouping="Tydzień"),1)
        self.assertEqual(len([n for n in z.namelist() if n.startswith("ppt/media/")]),1)
        self.assertIn("Jakość".encode(),z.read("ppt/slides/slide3.xml"))
    def test_invalid_selection_empty_and_overlong_title(self):
        for views in [(),(0,0),(3,),(True,)]:
            with self.subTest(views=views),self.assertRaises(ValueError):export_pptx(self.sample(),views)
        with self.assertRaises(ValueError):export_pptx(self.sample(categories=[]))
        with self.assertRaises(ValueError):export_pptx(self.sample(),title="x"*46)
