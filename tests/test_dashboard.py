"""Independent expectations for the dashboard contract, not derived from the engine."""
import json
import tempfile
import unittest
from pathlib import Path
from decimal import Decimal
from app.analysis import analyze, analyze_parsed, weekly_trend, ranked_categories
from app.validation import CsvProfile, load_csv
from app.pipeline import export_analysis
from app.pdf_report import percent

ROOT = Path(__file__).resolve().parents[1]
class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.profile=CsvProfile(allow_negative=True, amount_basis="netto")
        self.expected=json.loads((ROOT/"sample_data/dashboard_expected.json").read_text())
    def result(self, **kwargs):
        return analyze(ROOT/"sample_data/dashboard_reference.csv",profile=self.profile,
                       start_date="2026-09-03",end_date="2026-09-04",
                       coverage_start="2026-09-01",coverage_end="2026-09-04",**kwargs)
    def test_independent_all_and_filtered(self):
        for name,categories in [("all",None),("A",["A"])]:
            with self.subTest(name=name):
                r=self.result(categories=categories); e=self.expected[name]
                self.assertEqual(r["kpis"]["total_minor"],e["total_minor"])
                self.assertEqual(r["kpis"]["rows_cnt"],e["rows_cnt"])
                self.assertEqual(str(r["kpis"]["avg_value"]),e["avg_value"])
                self.assertEqual(r["comparison"]["previous"]["total_minor"],e["previous_minor"])
                self.assertEqual(r["comparison"]["difference"]["total_value"],Decimal(e["difference"]))
                self.assertEqual(percent(r["comparison"]["change_pct"]["total_value"]),e["change_display"])
    def test_reconciliation_and_quality(self):
        r=self.result()
        self.assertEqual([x["total_minor"] for x in r["daily"]],self.expected["daily_minor"])
        self.assertEqual({x["category"]:x["difference"] for x in r["categories"]},
                         {k:Decimal(v) for k,v in self.expected["category_differences"].items()})
        q=self.result(categories=["A"])["quality"]
        self.assertEqual((q["total_rows"],q["rows_outside_period"],q["rows_excluded_category"],q["rows_in_period"]),(6,3,1,2))
        self.assertEqual((q["negative_values"],q["view_negative_count"]),(1,0))
    def test_empty_selection_and_export_blocked(self):
        r=self.result(categories=[])
        self.assertEqual(r["status"],"empty")
        self.assertIsNone(r["kpis"]["avg_value"])
        self.assertFalse(r["comparison"]["baseline_available"])
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError): export_analysis(r,output_dir=d)
            self.assertEqual(list(Path(d).iterdir()),[])
    def test_unverified_and_gap(self):
        data=b"date,value,category\n2026-09-01,10,A\n2026-09-03,20,A\n"
        r=analyze(data,start_date="2026-09-01",end_date="2026-09-03")
        self.assertIsNone(r["daily"][1]["total_value"])
        self.assertIsNone(weekly_trend(r["daily"])[0]["total_value"])
        self.assertFalse(r["comparison"]["baseline_available"])
        full=analyze(data,start_date="2026-09-01",end_date="2026-09-03",
                     coverage_start="2026-09-01",coverage_end="2026-09-03")
        self.assertEqual(full["daily"][1]["total_value"],0)
        self.assertEqual(weekly_trend(full["daily"])[0]["total_value"],30)
    def test_zero_negative_base_and_missing_category(self):
        for base in ("0","-10"):
            data=f"date,value,category\n2026-09-01,{base},A\n2026-09-02,20,B\n".encode()
            r=analyze(data,profile=self.profile,start_date="2026-09-02",end_date="2026-09-02",
                      coverage_start="2026-09-01",coverage_end="2026-09-02")
            self.assertTrue(r["comparison"]["baseline_available"])
            self.assertIsNone(r["comparison"]["change_pct"]["total_value"])
            self.assertEqual(sum(x["difference"] for x in r["categories"]),Decimal(20)-Decimal(base))
            self.assertEqual({x["category"] for x in r["categories"]},{"A","B"})
    def test_duplicates_and_week_boundaries(self):
        data=b"date,value,category\n2026-09-06,0.10,A\n2026-09-06,0.10,A\n2026-09-07,0.11,B\n"
        r=analyze(data,start_date="2026-09-06",end_date="2026-09-07")
        self.assertEqual(r["kpis"]["total_minor"],31)
        self.assertEqual(r["quality"]["duplicate_rows"],1)
        self.assertEqual(len(weekly_trend(r["daily"])),2)
        self.assertEqual(r["kpis"]["avg_value"],Decimal("0.10"))
    def test_top_remainder_and_large_money(self):
        data=("date,value,category\n"+"".join(f"2026-09-01,{i}.01,C{i}\n" for i in range(12))).encode()
        r=analyze(data,start_date="2026-09-01",end_date="2026-09-01")
        top=ranked_categories(r)
        self.assertEqual(len(top),6)
        self.assertEqual(sum(i["total_minor"] for i in top),6612)
        data=("date,value,category\n"+"2026-09-01,10000000000,A\n"*10000+"2026-09-01,0.01,A\n").encode()
        self.assertEqual(analyze(data)["kpis"]["total_value"],Decimal("100000000000000.01"))
    def test_pdf_snapshot_matches_filters(self):
        r=self.result(categories=["A"])
        with tempfile.TemporaryDirectory() as d:
            pdf=Path(export_analysis(r,output_dir=d))
            s=json.loads((pdf.parent/"summary.json").read_text(encoding="utf-8"))
            self.assertEqual(s["kpis"]["total_minor"],40000)
            self.assertEqual(s["selected_categories"],["A"])
            self.assertEqual(s["source_sha256"],r["source_sha256"])
            self.assertNotIn("rows",s)
            self.assertTrue(pdf.read_bytes().startswith(b"%PDF"))
    def test_filters_do_not_mutate_source(self):
        p=load_csv(ROOT/"sample_data/dashboard_reference.csv",self.profile)
        before=[dict(r) for r in p.rows]
        analyze_parsed(p,profile=self.profile,categories=[])
        self.assertEqual(p.rows,before)
    def test_unrounded_mean_change(self):
        data=b"date,value,category\n2026-09-01,0.01,A\n2026-09-01,0.02,A\n2026-09-02,0.03,A\n2026-09-02,0.03,A\n"
        r=analyze(data,start_date="2026-09-02",end_date="2026-09-02",coverage_start="2026-09-01",coverage_end="2026-09-02")
        self.assertEqual(r["comparison"]["change_pct"]["avg_value"],100)
        self.assertEqual(r["comparison"]["difference"]["avg_value"],Decimal(".015"))
