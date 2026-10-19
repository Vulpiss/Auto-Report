"""Export synthetic PPTX test cases through the production exporter."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.analysis import analyze
from app.validation import CsvProfile
from app.presentation import export_pptx
r=analyze(ROOT/"sample_data/dashboard_reference.csv",profile=CsvProfile(allow_negative=True,amount_basis="netto"),
          start_date="2026-09-03",end_date="2026-09-04",coverage_start="2026-09-01",coverage_end="2026-09-04")
out=ROOT/"build/analyst-live"
(out/"qa.pptx").write_bytes(export_pptx(r,comment="Dane syntetyczne; przykład z ujemną pozycją."))
long="Kategoria: "+"Żółć wyposażenie "*10
data=("date,value,category\n"+"".join(f"2026-09-19,{i-4}.99,{long}{i}\n" for i in range(12))).encode()
r=analyze(data,profile=CsvProfile(allow_negative=True),start_date="2026-09-01",end_date="2026-09-19")
(out/"stress.pptx").write_bytes(export_pptx(r,(0,),title="Kontrola długiego tytułu i nazw kategorii",comment="Dane syntetyczne. Nie potwierdzono zakresu."))
print("QA: 3 slajdy + 1 stresowy, bez danych klientów")
