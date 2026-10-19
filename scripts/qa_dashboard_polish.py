"""Synthetic layout and reconciliation fixture; no real customer data."""
from pathlib import Path
import sys,csv,json
from decimal import Decimal
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.validation import CsvProfile
from app.analysis import analyze
from app.dashboard_model import make_model
from app.editable_presentation import export_editable
from app.presentation import export_pptx
from app.pipeline import export_analysis
out=Path("build/dashboard-polish");out.mkdir(parents=True,exist_ok=True)
source=out/"stress.csv"
expected=Decimal(0)
with source.open("w",encoding="utf-8-sig",newline="") as f:
 w=csv.writer(f);w.writerow(["date","value","category","product","customer","order"])
 for i in range(240):
  name=f"{i:03d} "+"Bardzo długa nazwa kategorii opakowań hurtowych "*3
  product=f"P{i:03d}-"+"X"*160
  prev=Decimal(i+1)*Decimal("900000.01")
  cur=Decimal(i+1)*Decimal("1000000.01")*(-1 if i%7==0 else 1)
  expected+=cur
  w.writerow(["2026-08-31",str(prev),name,product,f"C{i:03d}",f"OLD{i}"])
  w.writerow(["2026-09-07",str(cur),name,product,f"C{i:03d}",f"NEW{i}"])
p=CsvProfile(product_col="product",customer_col="customer",order_col="order",allow_negative=True)
(out/"stress.profile.json").write_text(json.dumps(p.to_dict(),indent=2),encoding="utf-8")
r=analyze(source,profile=p,start_date="2026-09-01",end_date="2026-09-07",coverage_start="2026-08-25",coverage_end="2026-09-07")
assert r["kpis"]["total_value"]==expected
m=make_model(r)
assert sum(x["value"] for x in m["changes"])==r["comparison"]["difference"]["total_value"]
assert sum(x["total_value"] for x in m["rank"])==expected
(out/"stress-native.pptx").write_bytes(export_editable(r,dimension="product",comment="Sztuczny test: 240 kategorii, duże kwoty, zwroty."))
(out/"stress-dashboard.pptx").write_bytes(export_pptx(r,comment="Sztuczny test układu i sum."))
pdf=export_analysis(r,output_dir=out/"pdf")
(out/"evidence.json").write_text(json.dumps(dict(categories=240,rows=480,total=str(expected),pdf=str(pdf),checks=["independent total","top plus rest reconciliation","change reconciliation"]),indent=2),encoding="utf-8")
print("STRESS PASS",pdf)
