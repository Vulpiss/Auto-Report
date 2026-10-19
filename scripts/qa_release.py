"""Synthetic demo, stress PDF, GUI thread checks and evidence."""
import argparse
import csv
import io
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Keep the QA profile and output strictly inside the project.
os.environ["AUTOREPORT_HOME"] = str(ROOT / "build" / "qa-home")

from app.pipeline import generate_report
from app.validation import CsvProfile, load_csv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui", action="store_true")
    args = parser.parse_args()
    qa = ROOT / "build" / "qa"
    qa.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    demo = generate_report(ROOT / "sample_data/pilot_demo.csv", 7,
                           output_dir=ROOT / "output/pdf",
                           profile=CsvProfile(amount_basis="netto"),
                           coverage_start="2026-08-31", coverage_end="2026-09-13",
                           title="Tygodniowy raport - dane syntetyczne")
    elapsed = time.perf_counter() - started
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["date", "value", "category"])
    for n in range(12):
        writer.writerow(["2026-09-13", "9999999.99", f"Kategoria {n:02d} - " + "Żółć, środki czystości i wyposażenie " * 4])
    stress = generate_report(stream.getvalue().encode(), 7, output_dir=qa,
                             title="Kontrola długich polskich kategorii i dużych wartości")
    count = 100_000
    large = "date,value,category\n" + "2026-09-13,0.01,Papier\n" * count
    started = time.perf_counter()
    parsed = load_csv(large.encode())
    large_elapsed = time.perf_counter() - started
    assert len(parsed.rows) == count and sum(r["value_minor"] for r in parsed.rows) == 100_000
    evidence = {"demo_pdf": demo, "stress_pdf": stress, "demo_generation_seconds": round(elapsed, 3),
                "large_input_rows": count, "large_parse_seconds": round(large_elapsed, 3),
                "large_total_minor": 100_000, "gui": "not_run"}
    if args.gui:
        import tkinter as tk
        from interfaces.desktop_app import AutoReportApp
        root = tk.Tk()
        root.withdraw()
        app = AutoReportApp(root)
        root.update_idletasks()
        app.csv_path.set(str(ROOT / "sample_data/pilot_demo.csv"))
        app.output_dir.set(str(qa / "gui"))
        app.run_report_threaded()
        assert app.busy
        app.run_report_threaded()  # Duplicate click must have no effect.
        deadline = time.monotonic() + 30
        while app.busy and time.monotonic() < deadline:
            root.update()
            time.sleep(.02)
        assert not app.busy and app.last_output, app.status.get()
        assert Path(app.last_output).is_file()
        first = app.last_output
        app.csv_path.set(str(ROOT / "does-not-exist.csv"))
        app.run_report_threaded()
        assert not app.busy and app.last_output == first
        app.save()
        root.destroy()
        evidence["gui"] = "passed: worker, duplicate click, result, missing file, profile save"
    (qa / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
