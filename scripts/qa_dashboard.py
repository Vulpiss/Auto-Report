"""Synthetic dashboard QA; never reads customer data or overwrites prior reports."""
import json
import subprocess
import sys
import time
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.analysis import analyze, analyze_parsed
from app.validation import CsvProfile, load_csv
from app.pipeline import export_analysis
from pypdf import PdfReader
out=ROOT/"build/dashboard-qa"
out.mkdir(parents=True,exist_ok=True)
profile=CsvProfile(allow_negative=True,amount_basis="netto")
r=analyze(ROOT/"sample_data/dashboard_reference.csv",profile=profile,start_date="2026-09-03",end_date="2026-09-04",
          coverage_start="2026-09-01",coverage_end="2026-09-04",categories=["A"])
pdf=Path(export_analysis(r,output_dir=out,title="Dashboard - kontrola kategorii A"))
text="\n".join(p.extract_text() for p in PdfReader(pdf).pages)
assert "400,00" in text and "Kategorie: A" in text and "200,00" in text
stress=("date,value,category\n"+"".join(f"2026-09-04,{n+1}.99,"+f"Kategoria {n:02} "+"Żółć wyposażenie "*10+"\n" for n in range(15))).encode()
s=analyze(stress,profile=profile)
stress_pdf=Path(export_analysis(s,output_dir=out,title="Kontrola długich nazw kategorii"))
for label,path in [("filtered",pdf),("stress",stress_pdf)]:
    subprocess.run(["pdftoppm","-scale-to","1400","-png",str(path),str(out/label)],check=True)
data=("date,value,category\n"+"2026-09-03,0.01,A\n"*50000+"2026-09-04,0.02,B\n"*50000).encode()
t=time.perf_counter(); parsed=load_csv(data,profile); r=analyze_parsed(parsed,profile=profile); import_s=time.perf_counter()-t
t=time.perf_counter(); filtered=analyze_parsed(parsed,profile=profile,categories=["A"]); filter_s=time.perf_counter()-t
assert r["kpis"]["total_minor"]==150000 and filtered["kpis"]["total_minor"]==50000
evidence=dict(rows=100000,import_and_analysis_seconds=round(import_s,4),filter_analysis_seconds=round(filter_s,4),
              import_target_seconds=10,filter_target_seconds=1,import_pass=import_s<=10,filter_pass=filter_s<=1,
              filtered_pdf=str(pdf),stress_pdf=str(stress_pdf),
              scope="Engine on this host; browser rendering and human time excluded.")
(out/"evidence.json").write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(evidence,ensure_ascii=False,indent=2))
