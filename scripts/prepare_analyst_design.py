"""Prepare synthetic, verified data for the dashboard design."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.analysis import analyze
from app.validation import CsvProfile
source=ROOT/"sample_data/pilot_demo.csv"
profile=CsvProfile(amount_basis="netto")
r=analyze(source,profile=profile,start_date="2026-09-07",end_date="2026-09-13",coverage_start="2026-08-31",coverage_end="2026-09-13")
p=analyze(source,profile=profile,start_date="2026-08-31",end_date="2026-09-06")
assert r["kpis"]["total_minor"]==125000
assert r["comparison"]["previous"]["total_minor"]==100000
assert {c["category"]:c["total_minor"] for c in r["categories"]}=={"Papier":55000,"Teczki i segregatory":45000,"Środki czystości":25000}
assert {c["category"]:c["difference"] for c in r["categories"]}=={"Papier":100,"Teczki i segregatory":150,"Środki czystości":0}
data=dict(current=r,previous_daily=p["daily"])
(ROOT/"build/analyst-design/data.json").write_text(json.dumps(data,ensure_ascii=False,default=str),encoding="utf-8")
print("Wzorzec makiety: 1250 PLN / 7 / 178.57; zmiana 250 PLN i 25%; kategorie 550/450/250 potwierdzone.")
