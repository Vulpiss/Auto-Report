"""Repeatable internal acceptance: synthetic inputs, two cycles, session/export checks."""
from pathlib import Path
import sys, json, io, hashlib, re
from dataclasses import replace
from decimal import Decimal
from zipfile import ZipFile
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.validation import CsvProfile, load_csv, DataValidationError
from app.analysis import analyze
from app.dashboard_model import make_model
from app.pipeline import export_analysis
from app.presentation import export_pptx
from app.editable_presentation import export_editable,C
from app.workspace import encode_session,decode_document,verify_source
from pypdf import PdfReader

def run():
    out=ROOT/"build/internal-acceptance"
    fixtures=ROOT/"sample_data/internal_acceptance"
    out.mkdir(parents=True,exist_ok=True); fixtures.mkdir(parents=True,exist_ok=True)
    baseline="date,value,category\n2026-09-01,10,A\n"
    cases={
      "empty":b"", "headers_only":b"date,value,category\n",
      "duplicate_headers":b"date,value,value\n2026-09-01,10,A\n",
      "missing_column":b"date,value\n2026-09-01,10\n",
      "extra_field":b"date,value,category\n2026-09-01,10,A,extra\n",
      "unclosed_quote":b'date,value,category\n2026-09-01,10,"A\n',
      "invalid_date":baseline.replace("2026-09-01","2026-02-30").encode(),
      "nan":baseline.replace(",10,",",NaN,").encode(),
      "missing_amount":baseline.replace(",10,",",,").encode(),
      "negative_without_rule":baseline.replace(",10,",",-10,").encode(),
      "excess_precision":baseline.replace(",10,",",10.123,").encode(),
      "missing_category":baseline.replace(",A",",").encode(),
      "wrong_encoding":"date,value,category\n2026-09-01,10,Żółć\n".encode("cp1250"),
      "mixed_valid_invalid":(baseline+"2026-09-02,broken,B\n").encode(),
    }
    evidence={"invalid_inputs":{},"cycles":[]}
    for name,raw in cases.items():
        (fixtures/(name+".csv")).write_bytes(raw)
        try: load_csv(raw)
        except DataValidationError as e:
            evidence["invalid_inputs"][name]={"blocked":True,"message":str(e)}
        else: raise AssertionError("Accepted invalid input: "+name)
    polish="date;value;category\n01.09.2026;10,25;Żółć\n02.09.2026;2,75;Łączniki\n".encode("cp1250")
    pp=CsvProfile(delimiter=";",decimal_separator=",",date_format="%d.%m.%Y",encoding="cp1250")
    (fixtures/"polish.csv").write_bytes(polish)
    (fixtures/"polish.profile.json").write_text(json.dumps(pp.to_dict(),ensure_ascii=False,indent=2),encoding="utf8")
    assert sum(x["value_minor"] for x in load_csv(polish,pp).rows)==1300
    dup=(baseline+"2026-09-01,10,A\n").encode()
    (fixtures/"duplicates.csv").write_bytes(dup)
    parsed=load_csv(dup)
    assert len(parsed.rows)==2 and parsed.quality["duplicate_rows"]==1
    assert sum(x["value_minor"] for x in parsed.rows)==2000

    header="date,value,category,quantity,order,product,customer,cost\n"
    previous="2026-08-31,100,A,2,O1,P1,C1,60\n2026-09-01,200,B,4,O2,P2,C2,140\n"
    week1="2026-09-07,150,A,3,N1,P1,C1,90\n2026-09-08,100,B,2,N1,P2,C1,80\n2026-09-09,350,A,7,N2,P1,C2,200\n"
    week2="2026-09-14,200,A,4,M1,P1,C1,120\n2026-09-15,-50,B,-1,M2,P2,C2,-35\n2026-09-16,550,A,11,M3,P1,C2,330\n"
    profile=CsvProfile(quantity_col="quantity",order_col="order",product_col="product",customer_col="customer",cost_col="cost",value_is_sales=True,quantity_unit="szt.",amount_basis="netto",allow_negative=True)
    (fixtures/"wholesale.profile.json").write_text(json.dumps(profile.to_dict(),indent=2),encoding="utf8")
    frozen={}
    for index,(content,start,end,total,prev,cost,orders,qty,change) in enumerate([
        (header+previous+week1,"2026-09-07","2026-09-13",600,300,370,2,12,[400,-100]),
        (header+previous+week1+week2,"2026-09-14","2026-09-20",700,600,415,3,14,[250,-150]),
    ],1):
        raw=content.encode()
        (fixtures/f"cycle{index}.csv").write_bytes(raw)
        state={"start":start,"end":end,"grouping":"Dzień","coverage_start":"2026-08-31","coverage_end":end,"comparison_mode":"Poprzedni okres"}
        session=encode_session(raw,profile,state)
        (fixtures/f"cycle{index}.session.json").write_bytes(session)
        doc=decode_document(session);verify_source(doc,raw)
        assert doc["settings"]==state and doc["profile"]==profile
        try:verify_source(doc,raw+b"\n")
        except ValueError:pass
        else:raise AssertionError("Changed CSV accepted for session")
        r=analyze(raw,profile=profile,start_date=start,end_date=end,coverage_start="2026-08-31",coverage_end=end)
        assert r["kpis"]["total_value"]==total
        assert r["comparison"]["previous"]["total_value"]==prev
        assert r["business"]["cost"]==cost and r["business"]["profit"]==total-cost
        assert r["business"]["orders"]==orders and r["business"]["quantity"]==qty
        model=make_model(r)
        assert sum(x["total_value"] for x in model["rank"])==total
        assert sum(x["value"] for x in model["changes"])==total-prev
        assert sorted(x["difference"] for x in r["dimensions"]["product"])==sorted(change)
        cycle=out/f"cycle{index}";cycle.mkdir(exist_ok=True)
        pdf=Path(export_analysis(r,output_dir=cycle/"pdf"))
        summary=json.loads(pdf.with_name("summary.json").read_text(encoding="utf8"))
        assert Decimal(summary["kpis"]["total_value"])==total
        assert summary["source_sha256"]==hashlib.sha256(raw).hexdigest()
        pdftext="\n".join(p.extract_text() for p in PdfReader(pdf).pages)
        assert f"{total},00" in pdftext and "PLN" in pdftext
        for style,exporter in [("dashboard",export_pptx),("native",export_editable)]:
            data=exporter(r)
            path=cycle/(style+".pptx");path.write_bytes(data)
            with ZipFile(io.BytesIO(data)) as z:
                slides=[n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml",n)]
                assert len(slides)==3 and z.testzip() is None
                notes="\n".join(z.read(n).decode() for n in z.namelist() if "/notesSlides/" in n and n.endswith(".xml"))
                assert start in notes and end in notes and "PLN" in notes
                if style=="native":
                    charts=[n for n in z.namelist() if re.search(r"/charts/chart\d+\.xml$",n)]
                    assert len(charts)==3
                    assert len([n for n in z.namelist() if n.endswith(".xlsx")])==3
                    changechart=ET.fromstring(z.read(next(n for n in charts if n.endswith("chart2.xml"))))
                    vals=[Decimal(x.text) for x in changechart.findall(".//{"+C+"}val//{"+C+"}pt/{"+C+"}v")]
                    assert sorted(vals)==sorted(change),(vals,change)
            frozen[str(path)]=hashlib.sha256(data).hexdigest()
        # Same snapshot exported again: independent location, unchanged semantics.
        again=Path(export_analysis(r,output_dir=cycle/"pdf"))
        assert again!=pdf and pdf.is_file()
        repeated=json.loads(again.with_name("summary.json").read_text(encoding="utf8"))
        assert repeated["kpis"]==summary["kpis"] and repeated["source_sha256"]==summary["source_sha256"]
        for path,digest in frozen.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
        evidence["cycles"].append({"cycle":index,"total":total,"previous":prev,"profit":total-cost,"orders":orders,"quantity":qty,"pdf":str(pdf),"pdf_pages":len(PdfReader(pdf).pages),"pptx_styles":2,"slides_per_style":3,"native_chart_values":change,"repeat_pdf_preserves_previous":True,"session_same_source":True,"session_changed_source_blocked":True})
    evidence["valid_inputs"]={"polish_cp1250_total":13,"duplicates_preserved_total":20}
    (out/"evidence.json").write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding="utf8")
    print(json.dumps(evidence,ensure_ascii=False,indent=2))
if __name__=="__main__":run()
