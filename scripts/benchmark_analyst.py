"""Bounded synthetic performance checks; no production database."""
from pathlib import Path
import sys,time,json,platform
from datetime import date,timedelta
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.analysis import analyze
from app.dashboard_model import make_model,table_page
from app.presentation import export_pptx
from app.validation import CsvProfile
out=Path("build/analyst-live/hardening");out.mkdir(parents=True,exist_ok=True)
evidence=[]
for count,categories,days,slides in [(100000,500,28,True),(10000,10000,366,False)]:
    origin=date(2024,1,1)
    raw=("date,value,category\n"+"".join(f"{origin+timedelta(days=i%(days*2))},1.01,K{i%categories:05}\n" for i in range(count))).encode()
    begin=origin+timedelta(days=days);end=origin+timedelta(days=days*2-1)
    t=time.perf_counter()
    r=analyze(raw,profile=CsvProfile(amount_basis="netto"),start_date=str(begin),end_date=str(end),coverage_start=str(origin),coverage_end=str(end))
    parsed=time.perf_counter()-t;t=time.perf_counter()
    m=make_model(r);page=table_page(r,m)
    modeled=time.perf_counter()-t
    expected=sum(101 for i in range(count) if i%(days*2)>=days)
    assert r["kpis"]["total_minor"]==expected
    assert sum(x["value"] for x in m["structure"])==r["kpis"]["total_value"]
    item=dict(rows=count,categories=categories,days=days,bytes=len(raw),analysis_s=round(parsed,3),model_and_page_s=round(modeled,3),visible_rows=len(page))
    if slides:
        t=time.perf_counter();(out/"performance.pptx").write_bytes(export_pptx(r));item["pptx_s"]=round(time.perf_counter()-t,3)
    evidence.append(item)
report=dict(platform=platform.platform(),python=platform.python_version(),cases=evidence,scope="Local synthetic run; not clean Windows or client pilot")
(out/"performance.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
