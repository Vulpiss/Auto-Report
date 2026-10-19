"""Regression contracts for analyst release hardening."""
import unittest
from decimal import Decimal
from app.analysis import analyze, ranked_categories
from app.dashboard_model import make_model, table_page
from app.validation import CsvProfile

class AnalystAcceptanceTests(unittest.TestCase):
    def test_group_names_do_not_merge_with_source_categories(self):
        names=["Pozostałe kategorie (grupa)","Pozostałe (grupa)","Pozostałe (3 kategorii)","D","E","F","G","H"]
        data="date,value,category\n"+"".join(f"2026-09-01,1,{c}\n2026-09-02,{80-i*10},{c}\n" for i,c in enumerate(names))
        r=analyze(data.encode(),start_date="2026-09-02",end_date="2026-09-02",coverage_start="2026-09-01",coverage_end="2026-09-02")
        m=make_model(r)
        self.assertEqual(len(m["category_labels"]),len(set(m["category_labels"])))
        self.assertNotIn(m["category_labels"][-1],names)
        self.assertEqual(len({x["category"] for x in m["changes"]}),len(m["changes"]))
        rank=ranked_categories(r)
        self.assertEqual(len({x["category"] for x in rank}),len(rank))
        self.assertEqual(sum(x["value"] for x in m["structure"]),360)
        self.assertEqual(sum(x["value"] for x in m["changes"]),352)

    def test_pagination_does_not_change_scope_and_handles_last_page(self):
        data="date,value,category\n"+"".join(f"2026-09-02,{i+1},C{i:03}\n" for i in range(205))
        r=analyze(data.encode(),start_date="2026-09-01",end_date="2026-09-02")
        m=make_model(r)
        self.assertEqual(r["kpis"]["total_value"],21115)
        self.assertNotIn("spark",m["table"][0])
        first=table_page(r,m)
        last=table_page(r,m,200)
        self.assertEqual((len(first),len(last)),(100,5))
        self.assertEqual(first[0]["spark"],[None,205.0])
        self.assertEqual(last[-1]["spark"],[None,1.0])
        self.assertEqual(len(m["table"]),205)
        with self.assertRaises(ValueError):table_page(r,m,-1)

    def test_three_successive_synthetic_exports_use_same_contract(self):
        # Explicit expectations, not recalculated by the production model.
        cases=[("2026-09-01","2026-09-02","100","120",12000,20),
               ("2026-09-03","2026-09-04","120","90",9000,-25),
               ("2026-09-05","2026-09-06","90","99",9900,10)]
        for previous,current,old,new,minor,pct in cases:
            with self.subTest(current=current):
                raw=f"date,value,category\n{previous},{old},Papier\n{current},{new},Papier\n".encode()
                r=analyze(raw,start_date=current,end_date=current,coverage_start=previous,coverage_end=current)
                self.assertEqual(r["kpis"]["total_minor"],minor)
                self.assertEqual(r["comparison"]["change_pct"]["total_value"],pct)

    def test_leap_day_and_equal_period_alignment(self):
        raw=b"date,value,category\n2024-02-27,1,A\n2024-02-28,2,A\n2024-02-29,3,A\n2024-03-01,4,A\n"
        r=analyze(raw,start_date="2024-02-29",end_date="2024-03-01",coverage_start="2024-02-27",coverage_end="2024-03-01")
        m=make_model(r)
        self.assertEqual([x["current"] for x in m["trend"]],[3,4])
        self.assertEqual([x["previous"] for x in m["trend"]],[1,2])

    def test_zero_day_and_gap_are_different(self):
        raw=b"date,value,category\n2026-09-01,100,A\n2026-09-03,5,A\n2026-09-03,-5,A\n"
        r=analyze(raw,profile=CsvProfile(allow_negative=True),start_date="2026-09-02",end_date="2026-09-03")
        self.assertEqual([x["rows_cnt"] for x in r["daily"]],[0,2])
        self.assertEqual([x["total_value"] for x in r["daily"]],[None,Decimal(0)])
