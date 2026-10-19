"""Generate three bounded PDF edge cases, then render every page for visual QA."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from uuid import uuid4
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.pipeline import generate_report
from scripts.hardening_fixtures import cases

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, default=ROOT / "output/pdf/local-hardening-2026-10-06")
args = parser.parse_args()
scratch = ROOT / "build/local-hardening" / ("pdf-" + uuid4().hex[:10])
scratch.mkdir(parents=True)
args.output.mkdir(parents=True, exist_ok=True)
renderer = shutil.which("pdftoppm")
if not renderer:
    raise SystemExit("Poppler pdftoppm required for visual QA")
evidence = []
for case in cases():
    (scratch / (case["name"] + ".csv")).write_bytes(case["raw"])
    pdf = Path(generate_report(case["raw"], profile=case["profile"], output_dir=scratch / case["name"], **case["options"]))
    summary = json.loads((pdf.parent / "summary.json").read_text(encoding="utf-8"))
    expected = case["expected"]
    assert summary["kpis"]["total_minor"] == expected["total_minor"]
    assert summary["kpis"]["rows_cnt"] == expected["rows"]
    assert summary["kpis"]["avg_value"] == expected["average"]
    if "previous_minor" in expected:
        assert summary["comparison"]["previous"]["total_minor"] == expected["previous_minor"]
    for key, value in expected.get("business", {}).items():
        assert str(summary["business"][key]) == str(value), (key, summary["business"][key])
    pages = [p.extract_text() for p in PdfReader(pdf).pages]
    assert len(pages) <= 4, "Unexpected page inflation"
    for token in case["pdf_tokens"]:
        assert token in "\n".join(pages), token
    for text in pages:
        if "Kategorie - najwyższe sumy i pozostałe" in text:
            assert "Kategoria" in text and "Suma [PLN]" in text, "Orphaned table heading"
    final = args.output / (case["name"] + ".pdf")
    shutil.copy2(pdf, final)
    render_dir = scratch / (case["name"] + "-render")
    render_dir.mkdir()
    subprocess.run([renderer, "-png", "-r", "120", str(final), str(render_dir / "page")], check=True)
    evidence.append(dict(case=case["name"], pages=len(pages), expected=expected,
                         pdf_sha256=hashlib.sha256(final.read_bytes()).hexdigest(),
                         rendered_pages=len(list(render_dir.glob("page-*.png"))), render_directory=str(render_dir)))
record = dict(date="2026-10-06", data="synthetic", template_version="4", cases=evidence,
              visual_review="pending: inspect every rendered page")
(scratch / "evidence.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(dict(result="PASS_NUMBERS_AND_RENDER", evidence=str(scratch / "evidence.json")), ensure_ascii=False))
