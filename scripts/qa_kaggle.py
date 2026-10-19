"""Verify an unchanged, locally downloaded Kaggle file against an independent CSV/Decimal calculation."""
from pathlib import Path
from io import StringIO
import sys,csv,json,hashlib,time,shutil
from datetime import datetime
from decimal import Decimal,ROUND_HALF_UP
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.validation import CsvProfile,load_csv,DataValidationError
from app.analysis import analyze
from app.dashboard_model import make_model
from app.presentation import export_pptx
from app.pipeline import export_analysis
source=Path("data/external/kaggle-supermarket/superstore/Sample - Superstore.csv")
out=Path("build/kaggle-qa");out.mkdir(parents=True,exist_ok=True)
raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest()
assert sha=="58fb59c63089e564d835e4aabe19d371757de1137a5bf1888243ae386c4b7a97","Dataset version changed; review expectations"
records=list(csv.DictReader(StringIO(raw.decode("cp1252"))))
independent=[(datetime.strptime(r["Order Date"],"%m/%d/%Y").strftime("%Y-%m-%d"),Decimal(r["Sales"]),r["Sub-Category"]) for r in records]
round2=lambda v:v.quantize(Decimal(".01"),rounding=ROUND_HALF_UP)
assert len(records)==9994
assert sum(v for _,v,_ in independent)==Decimal("2297200.8603")
assert sum(round2(v) for _,v,_ in independent)==Decimal("2297201.07")
profile=CsvProfile("Order Date","Sales","Sub-Category",encoding="cp1252",date_format="%m/%d/%Y",currency="XXX",amount_precision="half_up")
strict=CsvProfile(**dict(profile.to_dict(),amount_precision="strict"))
try:load_csv(raw,strict);raise AssertionError("Strict mode accepted excess precision")
except DataValidationError:pass
filters=dict(start_date="2017-10-01",end_date="2017-12-30")
r0=analyze(raw,profile=profile,**filters)
assert not r0["comparison"]["baseline_available"]
# This is a declared QA assumption about file coverage, NOT verified business completeness.
coverage=dict(coverage_start="2014-01-03",coverage_end="2017-12-30")
start=time.perf_counter();r=analyze(raw,profile=profile,**filters,**coverage);analysis_s=time.perf_counter()-start
current=[x for x in independent if "2017-10-01"<=x[0]<="2017-12-30"]
previous=[x for x in independent if "2017-07-02"<=x[0]<="2017-09-30"]
assert r["kpis"]["total_value"]==sum(round2(x[1]) for x in current)
assert r["kpis"]["rows_cnt"]==len(current)
assert r["comparison"]["previous"]["total_value"]==sum(round2(x[1]) for x in previous)
for grouping in ["Dzień","Tydzień"]:
    model=make_model(r,grouping)
    assert sum(t["current"] for t in model["trend"])==r["kpis"]["total_value"]
    assert sum(x["value"] for x in model["structure"])==r["kpis"]["total_value"]
    assert sum(x["value"] for x in model["changes"])==r["comparison"]["difference"]["total_value"]
for cat in sorted({x[2] for x in independent}):
    actual=analyze(raw,profile=profile,categories=[cat],**filters,**coverage)
    expected=[x for x in current if x[2]==cat]
    assert actual["kpis"]["rows_cnt"]==len(expected)
    assert actual["kpis"]["total_value"]==sum(round2(x[1]) for x in expected)
start=time.perf_counter()
(out/"report.pptx").write_bytes(export_pptx(r,title="Kaggle Superstore",comment="Test pliku. Kompletność przyjęta wyłącznie do porównania w teście."))
(out/"single.pptx").write_bytes(export_pptx(r,(2,),comment="Test pliku; kompletność jest założeniem."))
pptx_s=time.perf_counter()-start
pdf=Path(export_analysis(r,output_dir=out/"pdf",title="Kaggle Superstore — test CSV"))
shutil.copy2(pdf,out/"report.pdf")
from pypdf import PdfReader
text="\n".join(p.extract_text() for p in PdfReader(pdf).pages)
assert "PLN" not in text and "HALF_UP" in text and "Waluta nieokreślona" in text
report=dict(source_sha256=sha,records=len(records),categories=len({x[2] for x in independent}),profile=profile.to_dict(),
current=r["kpis"],previous=r["comparison"]["previous"],change=r["comparison"]["change_pct"],quality=r["quality"],
analysis_s=round(analysis_s,3),exports_3_plus_1_s=round(pptx_s,3),pdf_pages=len(PdfReader(pdf).pages),
coverage_assumption="Only for this QA exercise. Not proof of real business completeness.",
checks=["original bytes unchanged","strict rejects extra precision","unknown coverage suppresses comparisons","independent amounts and counts","17 category filters","daily and weekly reconciliation","PDF currency and rounding note","PPTX 1/3 slides"])
(out/"evidence.json").write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k not in ["quality","profile"]},ensure_ascii=False,indent=2,default=str))
