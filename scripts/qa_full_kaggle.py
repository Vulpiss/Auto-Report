"""Full unchanged Kaggle source QA. Run from repository root."""
import csv,io,json,time,sys,hashlib,ctypes
from pathlib import Path
from decimal import Decimal,ROUND_HALF_UP
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.validation import CsvProfile,load_csv
from app.analysis import analyze_parsed
from app.dashboard_model import make_model
p=CsvProfile(date_col="InvoiceDate",value_col="UnitPrice",category_col="Country",quantity_col="Quantity",order_col="InvoiceNo",product_col="StockCode",customer_col="CustomerID",quantity_unit="szt.",encoding="cp1252",date_format="%m/%d/%Y %H:%M",currency="XXX",value_mode="unit_price",amount_precision="half_up",allow_negative=True)
path=Path("data/external/kaggle-large/data.csv");out=Path("build/full-kaggle-qa");out.mkdir(parents=True,exist_ok=True)
t=time.perf_counter();parsed=load_csv(path,p);load_s=time.perf_counter()-t
assert len(parsed.rows)==541909
total=Decimal(0);count=0;orders=set();quantity=Decimal(0)
with path.open(encoding="cp1252",newline="") as f:
 for row in csv.DictReader(f):
  day=datetime.strptime(row["InvoiceDate"],"%m/%d/%Y %H:%M").date().isoformat()
  if "2011-01-01"<=day<="2011-12-09":
   total+=(Decimal(row["Quantity"])*Decimal(row["UnitPrice"])).quantize(Decimal(".01"),rounding=ROUND_HALF_UP)
   quantity+=Decimal(row["Quantity"]);count+=1;orders.add(row["InvoiceNo"])
t=time.perf_counter();r=analyze_parsed(parsed,profile=p,start_date="2011-01-01",end_date="2011-12-09");analysis_s=time.perf_counter()-t
assert r["kpis"]["total_value"]==total and r["kpis"]["rows_cnt"]==count
assert r["business"]["quantity"]==quantity and r["business"]["orders"]==len(orders)
models={}
for g in ("Dzień","Tydzień","Miesiąc"):
 t=time.perf_counter();m=make_model(r,g);models[g]=time.perf_counter()-t
 assert sum(x["rows_cnt"] for x in m["trend"])==count
assert not r["comparison"]["baseline_available"]
# Windows process peak working set, includes libraries, parsed data and analysis.
from ctypes import wintypes
class Memory(ctypes.Structure):
 _fields_=[("cb",wintypes.DWORD),("PageFaultCount",wintypes.DWORD)]+[(n,ctypes.c_size_t) for n in ("PeakWorkingSetSize","WorkingSetSize","QuotaPeakPagedPoolUsage","QuotaPagedPoolUsage","QuotaPeakNonPagedPoolUsage","QuotaNonPagedPoolUsage","PagefileUsage","PeakPagefileUsage")]
mem=Memory();mem.cb=ctypes.sizeof(mem)
ctypes.windll.kernel32.GetCurrentProcess.restype=wintypes.HANDLE
ctypes.windll.psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Memory),wintypes.DWORD]
assert ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),ctypes.byref(mem),mem.cb)
e=dict(source_rows=len(parsed.rows),source_bytes=path.stat().st_size,sha256=parsed.source_sha256,import_s=load_s,analysis_s=analysis_s,models_s=models,peak_working_set_mib=mem.PeakWorkingSetSize/1048576,period=["2011-01-01","2011-12-09"],expected_total=str(total),period_rows=count,invoices=len(orders),quantity=str(quantity),quality=parsed.quality,checks="Full original import; independent Decimal totals, quantities, invoice count; models in all three groupings; unknown coverage preserved")
(out/"evidence.json").write_text(json.dumps(e,ensure_ascii=False,indent=2),encoding="utf-8")
(out/"profile.json").write_text(json.dumps(p.to_dict(),indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in e.items() if k!="quality"},ensure_ascii=False,indent=2))
