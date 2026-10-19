"""Reproducible large Kaggle boundary and numerical QA; no production limits changed."""
from pathlib import Path
import sys,csv,json,hashlib,time,zipfile,io,shutil
from datetime import datetime
from decimal import Decimal,ROUND_HALF_UP
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.validation import CsvProfile,load_csv,DataValidationError
from app.analysis import analyze_parsed
from app.dashboard_model import make_model
from app.pipeline import export_analysis
from app.editable_presentation import export_editable
root=Path("data/external/kaggle-large"); out=Path("build/large-kaggle-qa")
out.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(root/"download.zip") as z:
    assert z.getinfo("data.csv").file_size<100_000_000
    raw=z.read("data.csv")
(root/"data.csv").write_bytes(raw)
e={"source_url":"https://www.kaggle.com/datasets/carrie1/ecommerce-data","source_bytes":len(raw),"source_sha256":hashlib.sha256(raw).hexdigest(),"timings_seconds":{},"checks":[]}
def timed(name,fn):
    t=time.perf_counter();v=fn();e["timings_seconds"][name]=round(time.perf_counter()-t,3);return v
def rejected(name,data,profile,match):
    try:timed(name,lambda:load_csv(data,profile))
    except DataValidationError as ex:
        assert match in str(ex),str(ex)
        e[name]=str(ex);e["checks"].append(name);return
    raise AssertionError(name+" accepted")
p=CsvProfile(quantity_col="quantity",order_col="order",product_col="product",customer_col="customer",quantity_unit="szt.",currency="XXX",allow_negative=True,amount_precision="half_up")
rejected("full_file_rejected",raw,p,"20")
selected=[]; count=0; blank=0; negatives=0
reader=csv.DictReader(io.StringIO(raw.decode("cp1252"),newline=""))
for row in reader:
    if not row: continue
    count+=1
    blank+=not bool(row["CustomerID"].strip())
    negatives+=Decimal(row["Quantity"])<0
    if count<=100001:selected.append(row)
e.update(source_rows=count,source_missing_customer=blank,source_negative_quantity=negatives)
converted=[]
for row in selected:
    converted.append(dict(date=datetime.strptime(row["InvoiceDate"],"%m/%d/%Y %H:%M").date().isoformat(),
        value=str(Decimal(row["Quantity"])*Decimal(row["UnitPrice"])),category=row["Country"],
        quantity=row["Quantity"],order=row["InvoiceNo"],product=row["StockCode"],customer=row["CustomerID"]))
def encode(rows):
    s=io.StringIO(newline="");w=csv.DictWriter(s,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);return s.getvalue().encode("utf-8-sig")
over=encode(converted)
rejected("row_limit_rejected",over,p,"100000")
sample=converted[:100000]; data=encode(sample)
(root/"sample-100000.csv").write_bytes(data)
(root/"sample-100000.profile.json").write_text(json.dumps(p.to_dict(),ensure_ascii=False,indent=2),encoding="utf-8")
parsed=timed("import_100000",lambda:load_csv(data,p))
lo=min(r["date"] for r in sample);hi=max(r["date"] for r in sample)
r=timed("analysis_100000",lambda:analyze_parsed(parsed,profile=p,start_date=lo,end_date=hi))
expect=sum((Decimal(x["value"]).quantize(Decimal(".01"),rounding=ROUND_HALF_UP) for x in sample),Decimal(0))
assert r["kpis"]["total_value"]==expect
assert r["kpis"]["rows_cnt"]==100000
assert r["business"]["quantity"]==sum(Decimal(x["Quantity"]) for x in selected[:100000])
assert r["business"]["orders"]==len({x["InvoiceNo"] for x in selected[:100000]})
assert r["business"]["profit"] is None
assert not r["comparison"]["baseline_available"]
e["checks"]+=["independent_total","independent_quantity","independent_invoice_count","unknown_profit_not_zero","unknown_coverage_disables_comparison"]
for group in ("Dzień","Tydzień","Miesiąc"):
    m=timed("model_"+group,lambda:make_model(r,group))
    assert len(m["cards"])==3
    assert sum(x["rows_cnt"] for x in m["trend"])==100000
e["checks"].append("three_models_and_groupings")
for country in sorted({x["category"] for x in sample}):
    f=analyze_parsed(parsed,profile=p,start_date=lo,end_date=hi,categories=[country])
    assert f["kpis"]["total_value"]==sum((Decimal(x["value"]).quantize(Decimal(".01"),rounding=ROUND_HALF_UP) for x in sample if x["category"]==country),Decimal(0))
e["checks"].append("all_country_filters")
ppt=timed("editable_pptx",lambda:export_editable(r,title="Kaggle: 100 000 pozycji",comment="Pierwsze 100 000 rekordów; wartość = ilość × cena. Waluta i kompletność niepotwierdzone."))
(out/"report.pptx").write_bytes(ppt)
with zipfile.ZipFile(io.BytesIO(ppt)) as z:
    assert z.testzip() is None
    assert len([n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")])==3
e["checks"].append("pptx_three_slides_zip_integrity")
pdf=timed("pdf_export",lambda:export_analysis(r,output_dir=out/"pdf",title="Kaggle: próbka 100 000 pozycji"))
shutil.copy2(pdf,out/"report.pdf")
from pypdf import PdfReader
e.update(sample_rows=100000,sample_bytes=len(data),sample_date_range=[lo,hi],sample_total=str(expect),sample_business=r["business"],sample_quality=parsed.quality,pdf_pages=len(PdfReader(pdf).pages),profile=p.to_dict(),
transformation="First 100000 source records, no deduplication or row removal. InvoiceDate explicitly reduced to date; value=Decimal(Quantity)*Decimal(UnitPrice), per-row HALF_UP to 2 decimals in importer. Country used as category. Currency unknown. Invoice IDs include cancellations; not a count of completed sales orders. Coverage unknown. No full-dataset analysis.")
(out/"evidence.json").write_text(json.dumps(e,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
print(json.dumps({k:v for k,v in e.items() if k not in ("sample_quality","profile")},ensure_ascii=False,indent=2,default=str))
