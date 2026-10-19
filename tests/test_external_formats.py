import unittest, tempfile, json, zipfile
from pathlib import Path
from io import BytesIO
from decimal import Decimal
from app.validation import CsvProfile,DataValidationError,load_csv,parse_date,parse_minor
from app.analysis import analyze
from app.dashboard_model import make_model
from app.presentation import export_pptx
from app.pipeline import export_analysis
from app.profiles import load_profile,save_profile

class ExternalFormatTests(unittest.TestCase):
    def test_date_order_is_explicit(self):
        self.assertEqual(parse_date("1/12/2017","%m/%d/%Y"),"2017-01-12")
        self.assertEqual(parse_date("1/12/2017","%d/%m/%Y"),"2017-12-01")
        self.assertEqual(parse_date("2/29/2024","%m/%d/%Y"),"2024-02-29")
        for value in ("2/29/2023","13/1/2017","1/1/17"):
            with self.assertRaises(ValueError):parse_date(value,"%m/%d/%Y")

    def test_cp1252_original_columns_and_precision(self):
        raw="Order Date,Sales,Sub-Category,Ignored\n1/13/2017,1.235,Café,x\n".encode("cp1252")
        p=CsvProfile("Order Date","Sales","Sub-Category",encoding="cp1252",date_format="%m/%d/%Y",currency="XXX")
        with self.assertRaises(DataValidationError):load_csv(raw,p)
        p=CsvProfile(**dict(p.to_dict(),amount_precision="half_up"))
        parsed=load_csv(raw,p)
        self.assertEqual(parsed.rows[0]["value_minor"],124)
        self.assertEqual(parsed.rows[0]["category"],"Café")
        self.assertEqual(parsed.quality["rounded_rows"],1)
        self.assertEqual(Decimal(parsed.quality["rounding_delta"]),Decimal(".005"))

    def test_rounding_is_opt_in_and_not_truncation(self):
        with self.assertRaises(ValueError):parse_minor("1.235")
        self.assertEqual(parse_minor("1.235",amount_precision="half_up"),124)
        self.assertEqual(parse_minor("-1.235",allow_negative=True,amount_precision="half_up"),-124)
        with self.assertRaises(ValueError):parse_minor("-0.001",amount_precision="half_up")
        for value in ("NaN","1e3","1,000.25","10000000000.001"):
            with self.assertRaises(ValueError):parse_minor(value,amount_precision="half_up")

    def test_rounding_does_not_invent_duplicates(self):
        raw=b"date,value,category\n2026-09-01,1.231,A\n2026-09-01,1.232,A\n2026-09-02,2.235,B\n"
        r=analyze(raw,profile=CsvProfile(amount_precision="half_up",currency="USD"),start_date="2026-09-02",end_date="2026-09-02")
        self.assertEqual(r["quality"]["duplicate_rows"],0)
        self.assertEqual(r["quality"]["rounded_rows"],3)
        self.assertEqual(Decimal(r["quality"]["rounding_delta"]),Decimal(".002"))
        self.assertEqual(Decimal(r["quality"]["view_rounding_delta"]),Decimal(".005"))
        self.assertEqual(r["quality"]["view_rounded_rows"],1)
        self.assertEqual(r["kpis"]["total_minor"],224)

    def test_currency_survives_all_exports(self):
        from pypdf import PdfReader
        r=analyze(b"date,value,category\n2026-09-01,12.34,A\n",profile=CsvProfile(currency="USD"))
        self.assertIn("USD",make_model(r)["cards"][0][0][0])
        with tempfile.TemporaryDirectory() as tmp:
            pdf=export_analysis(r,output_dir=tmp)
            text="".join(p.extract_text() for p in PdfReader(pdf).pages)
            self.assertIn("USD",text)
            self.assertNotIn("PLN",text)
        with zipfile.ZipFile(BytesIO(export_pptx(r,(0,)))) as z:
            self.assertIn(b"USD",z.read("ppt/slides/slide1.xml"))
            self.assertNotIn(b"PLN",z.read("ppt/slides/slide1.xml"))

    def test_unknown_currency_and_saved_profile(self):
        p=CsvProfile(currency="XXX",encoding="cp1252",date_format="%m/%d/%Y",amount_precision="half_up")
        r=analyze(b"date,value,category\n1/1/2026,12.345,A\n",profile=p)
        self.assertIn("j.p.",make_model(r)["cards"][0][0][0])
        self.assertTrue(any("Waluta nieokreślona" in note for note in r["notes"]))
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"profile.json";save_profile(p,f);self.assertEqual(load_profile(f),p)

    def test_invalid_precision_and_currency(self):
        for p in (CsvProfile(amount_precision="silent"),CsvProfile(currency="USD/EUR"),CsvProfile(encoding="latin1")):
            with self.assertRaises(DataValidationError):p.validate()
