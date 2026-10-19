"""Run with the bundled Python (pypdf installed), after qa_release.py."""
from pathlib import Path
import json
from pypdf import PdfReader

root = Path(__file__).resolve().parents[1]
evidence = json.loads((root / "build/qa/evidence.json").read_text(encoding="utf-8"))
reader = PdfReader(evidence["demo_pdf"])
text = "\n".join(page.extract_text() or "" for page in reader.pages)
for expected in ["1 250,00", "178,57", "+25,0%", "Środki czystości", "550,00", "450,00", "250,00"]:
    assert expected in text, expected
assert len(reader.pages) == 2
assert "SCALE" not in text
stress = PdfReader(evidence["stress_pdf"])
stress_text = "\n".join(page.extract_text() or "" for page in stress.pages)
for n in range(10):
    assert f"Kategoria {n:02d}" in stress_text
assert "119 999 999,88" in stress_text
print(json.dumps({"demo_pages": len(reader.pages), "stress_pages": len(stress.pages), "text_checks": "passed"}, indent=2))
