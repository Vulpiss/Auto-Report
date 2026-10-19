import io,json,unittest
from dataclasses import replace
from decimal import Decimal
from zipfile import ZipFile
from xml.etree import ElementTree as E
from app.validation import CsvProfile,load_csv,DataValidationError
from app.analysis import analyze
from app.dashboard_model import make_model
from app.workspace import preview,propose,encode_session,decode_document,verify_source
from app.editable_presentation import export_editable,C
CSV=b"date,value,category,quantity,order,product,customer,cost\n2025-09-01,100,A,2,O1,P1,C1,60\n2025-09-02,200,B,4,O2,P2,C2,140\n2026-09-01,150,A,3,N1,P1,C1,90\n2026-09-02,100,B,2,N1,P2,C1,80\n2026-09-03,350,A,7,N2,P1,C2,200\n"
PROFILE=CsvProfile(quantity_col="quantity",order_col="order",product_col="product",customer_col="customer",cost_col="cost",value_is_sales=True,quantity_unit="szt.",amount_basis="netto")
def result(raw=CSV,profile=PROFILE,**extra):
    return analyze(raw,profile=profile,start_date="2026-09-01",end_date="2026-09-03",coverage_start="2025-09-01",coverage_end="2026-09-30",comparison_mode="Rok do roku",**extra)
class BusinessTests(unittest.TestCase):
    def test_independent_business_totals(self):
        r=result();b=r["business"]
        self.assertEqual(r["kpis"]["total_value"],600)
        self.assertEqual(b["orders"],2);self.assertEqual(b["average_order"],300)
        self.assertEqual(b["quantity"],12);self.assertEqual(b["cost"],370);self.assertEqual(b["profit"],230)
        self.assertEqual(b["margin_pct"],Decimal(23000)/600)
        self.assertEqual(r["comparison"]["difference"]["total_value"],300)
        p={x["entity"]:x["difference"] for x in r["dimensions"]["product"]}
        self.assertEqual(p,{"P1":Decimal(400),"P2":Decimal(-100)})
        self.assertEqual(sum(x["difference"] for x in r["dimensions"]["customer"]),300)
    def test_filters_scope_all_metrics(self):
        r=result(products=["P1"],customers=["C1"])
        self.assertEqual(r["kpis"]["total_value"],150);self.assertEqual(r["business"]["orders"],1)
        self.assertEqual(r["business"]["quantity"],3);self.assertEqual(r["business"]["profit"],60)
        self.assertEqual(r["comparison"]["previous"]["total_value"],100)
        self.assertEqual(r["quality"]["rows_excluded_category"],2)
    def test_missing_optional_does_not_become_zero(self):
        raw=CSV.replace(b"150,A,3,N1,P1,C1,90",b"150,A,,N1,P1,C1,")
        r=result(raw)
        self.assertIsNone(r["business"]["quantity"]);self.assertIsNone(r["business"]["profit"])
        self.assertIsNone(r["business"]["cost"]);self.assertEqual(r["business"]["orders"],2)
        self.assertEqual(r["quality"]["optional_missing"],{"quantity":1,"cost_minor":1})
    def test_invalid_optional_blocks_and_no_hidden_rounding(self):
        for raw in (CSV.replace(b",90\n",b",NaN\n"),CSV.replace(b",90\n",b",90.123\n"),CSV.replace(b",3,N1",b",abc,N1")):
            with self.assertRaises(DataValidationError):result(raw)
        r=result(CSV.replace(b",90\n",b",90.125\n"),replace(PROFILE,amount_precision="half_up"))
        self.assertEqual(r["business"]["cost"],Decimal("370.13"))
        self.assertEqual(r["quality"]["optional_rounding"]["cost_minor"],{"rows":1,"delta":"0.005"})
    def test_profit_negative_and_semantics(self):
        p=replace(PROFILE,cost_col="",profit_col="cost",value_is_sales=False)
        r=result(CSV.replace(b",90\n",b",-90\n"),p)
        self.assertEqual(r["business"]["profit"],190);self.assertIsNone(r["business"]["margin_pct"])
        r=result(profile=replace(PROFILE,value_is_sales=False))
        self.assertIsNone(r["business"]["profit"])
        with self.assertRaises(DataValidationError):replace(PROFILE,profit_col="profit").validate()
        with self.assertRaises(DataValidationError):replace(PROFILE,quantity_unit="").validate()
        with self.assertRaises(DataValidationError):replace(PROFILE,order_col="value").validate()
    def test_order_ids_not_row_counts_and_missing_disables(self):
        r=result(CSV.replace(b"100,B,2,N1",b"100,B,2,"))
        self.assertIsNone(r["business"]["orders"]);self.assertIsNone(r["business"]["average_order"])
    def test_months_and_year_comparison(self):
        raw=b"date,value,category\n2025-01-01,50,A\n2025-02-01,20,A\n2026-01-01,100,A\n2026-02-01,30,A\n"
        r=analyze(raw,start_date="2026-01-01",end_date="2026-02-28",comparison_mode="Rok do roku",coverage_start="2025-01-01",coverage_end="2026-02-28")
        t=make_model(r,"Miesiąc")["trend"]
        self.assertEqual([x["current"] for x in t],[100,30])
        self.assertEqual([x["previous"] for x in t],[50,20])
        self.assertEqual(sum(x["current"] for x in t),130)
        with self.assertRaisesRegex(ValueError,"29 lutego"):
            analyze(raw,start_date="2024-02-01",end_date="2024-02-29",comparison_mode="Rok do roku")
    def test_preview_and_explicit_mapping(self):
        headers,rows=preview(CSV,"utf-8-sig",",")
        self.assertEqual(len(rows),5);self.assertEqual(propose(headers)["value_col"],"value")
    def test_session_roundtrip_and_source_mismatch(self):
        state={"start":"2026-09-01","end":"2026-09-03","grouping":"Miesiąc","comparison_mode":"Rok do roku","product_filter":["P1"],"pptx_comment":"Test"}
        data=encode_session(CSV,PROFILE,state);doc=decode_document(data)
        verify_source(doc,CSV)
        self.assertEqual(doc["profile"],PROFILE);self.assertEqual(doc["settings"],state)
        with self.assertRaises(ValueError):verify_source(doc,CSV+b"\n")
        malformed=json.loads(data);malformed["settings"]["grouping"]="bad"
        with self.assertRaises(ValueError):decode_document(json.dumps(malformed).encode())
    def test_editable_workbook_and_selection(self):
        for views in ((0,1,2),(1,)):
            data=export_editable(result(),views,dimension="product")
            with ZipFile(io.BytesIO(data)) as z:
                chartnames=[n for n in z.namelist() if n.endswith(".xml") and "/charts/chart" in n]
                self.assertEqual(len(chartnames),len(views))
                self.assertEqual(len([n for n in z.namelist() if n.endswith(".xlsx")]),len(views))
                change=E.fromstring(z.read("ppt/slides/charts/chart2.xml"))
                values=[Decimal(n.text) for n in change.findall(".//{"+C+"}val//{"+C+"}pt/{"+C+"}v")]
                self.assertEqual(values,[400,-100])
                for name in [n for n in z.namelist() if n.endswith(".xlsx")]:
                    with ZipFile(io.BytesIO(z.read(name))) as book:self.assertIsNone(book.testzip())
    def test_no_coverage_keeps_gaps_in_native_chart(self):
        r=analyze(CSV,profile=PROFILE,start_date="2026-09-01",end_date="2026-09-05")
        with ZipFile(io.BytesIO(export_editable(r,(0,)))) as z:
            root=E.fromstring(z.read("ppt/slides/charts/chart1.xml"))
            self.assertEqual(len(root.findall(".//{"+C+"}ser")),1)
            values=root.findall(".//{"+C+"}val//{"+C+"}pt")
            self.assertEqual(len(values),3) # Only known dates, rendered as bars; never invented zero.
            self.assertIsNotNone(root.find(".//{"+C+"}barChart"))
