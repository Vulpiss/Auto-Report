"""Record a synthetic demonstration and verify exports in an isolated session.

The reference calculation deliberately uses csv/Decimal, without app analysis.
Browser automation and ffmpeg are authoring tools, not application dependencies.
"""
import argparse
import csv
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reference(raw):
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))

    def summarize(start, end):
        chosen = [r for r in rows if start <= r["date"] <= end]
        total = sum((Decimal(r["value"]) for r in chosen), Decimal("0"))
        categories = {}
        for row in chosen:
            categories[row["category"]] = categories.get(row["category"], Decimal("0")) + Decimal(row["value"])
        return dict(start=start, end=end, rows=len(chosen), total=f"{total:.2f}",
                    average=f"{(total / len(chosen)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP):.2f}",
                    categories={k: f"{v:.2f}" for k, v in sorted(categories.items())})

    full = summarize("2026-08-31", "2026-09-13")
    current = summarize("2026-09-07", "2026-09-13")
    previous = summarize("2026-08-31", "2026-09-06")
    # Fixed independent expectations also catch an accidental change to the fixture.
    assert (full["rows"], full["total"], full["average"]) == (14, "2250.00", "160.71")
    assert (current["rows"], current["total"], current["average"]) == (7, "1250.00", "178.57")
    assert previous["total"] == "1000.00"
    return dict(data_kind="synthetic", currency="PLN", amount_basis="nieokreślona",
                full=full, current=current, previous=previous,
                comparison_in_simple_mode="unavailable: export completeness not declared",
                change_if_both_periods_confirmed_complete="25.00%",
                bad_fields=[dict(csv_line=10, column="value", value="abc"),
                            dict(csv_line=14, column="category", value="")])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path)
    parser.add_argument("--ffmpeg", type=Path, help="Existing encoder binary; needed to record material")
    parser.add_argument("--verify-only", action="store_true", help="Validate a session without replacing portfolio media")
    parser.add_argument("--date", default="2026-10-04", help="Client date recorded in new QA evidence")
    args = parser.parse_args()
    if not args.verify_only and (not args.ffmpeg or not args.ffmpeg.is_file()):
        parser.error("Recording requires --ffmpeg pointing to an existing executable")
    if args.exe and not args.exe.is_file():
        parser.error("EXE does not exist")
    out = ROOT / "build/portfolio" / ("session-" + uuid4().hex[:10])
    out.mkdir(parents=True)
    portfolio = ROOT / "docs/portfolio"
    media = portfolio / "media"
    media.mkdir(parents=True, exist_ok=True)
    raw = (ROOT / "sample_data/pilot_demo.csv").read_bytes()
    original_hash = hashlib.sha256(raw).hexdigest()
    expected = reference(raw)
    expected["source_sha256"] = original_hash
    (out / "corrected.csv").write_bytes(raw)
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    rows[8]["value"] = "abc"
    rows[12]["category"] = ""
    with (out / "bad.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "value", "category"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    env = dict(os.environ, AUTOREPORT_PROFILE_DIR=str(out / "profiles"), PYTHONDONTWRITEBYTECODE="1")
    # This prepared format is described explicitly in DEMO.md, never a user profile.
    os.environ["AUTOREPORT_PROFILE_DIR"] = env["AUTOREPORT_PROFILE_DIR"]
    from app.profile_library import remember
    from app.validation import CsvProfile
    remember(["date", "value", "category"], CsvProfile())
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node is required for browser verification")
    if not args.verify_only:
        registry = json.loads(subprocess.check_output(
            [node, "-e", "const p=process.env.AUTOREPORT_PLAYWRIGHT_DIR || 'C:/Users/kompu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'; const path=require('path'); const b=require(path.join(path.dirname(require.resolve(p + '/package.json')), '../playwright-core/browsers.json')); console.log(JSON.stringify(b.browsers.find(x=>x.name==='ffmpeg')));"],
            env=env, text=True))
        cache = ROOT / "build/portfolio/runtime/browsers"
        encoder = cache / ("ffmpeg-" + registry["revision"]) / ("ffmpeg-win64.exe" if os.name == "nt" else "ffmpeg-linux")
        encoder.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.ffmpeg, encoder)
        env["PLAYWRIGHT_BROWSERS_PATH"] = str(cache)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    command = ([str(args.exe.resolve()), "--serve", str(port), "--log", str(out / "exe.log")] if args.exe else
               [sys.executable, "-B", "-m", "streamlit", "run", str(ROOT / "interfaces/simple_app.py"),
                "--server.address=127.0.0.1", f"--server.port={port}", "--server.headless=true",
                "--browser.gatherUsageStats=false", "--server.fileWatcherType=none"])
    url = f"http://127.0.0.1:{port}"
    with (out / "server.log").open("w", encoding="utf-8") as log:
        child = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=log,
                                 creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        try:
            deadline = time.monotonic() + 60
            while True:
                if child.poll() is not None:
                    raise RuntimeError("Demo server stopped; see " + str(out / "server.log"))
                try:
                    with urllib.request.urlopen(url + "/_stcore/health", timeout=1) as response:
                        if response.status == 200:
                            break
                except OSError:
                    if time.monotonic() > deadline:
                        raise TimeoutError("Demo server did not start")
                    time.sleep(.25)
            subprocess.run([node, str(ROOT / "scripts/qa_portfolio_browser.cjs"), url, str(out),
                            str(media), "verify" if args.verify_only else "record"],
                           cwd=ROOT, env=env, check=True, timeout=240)
        finally:
            child.terminate()
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=10)

    problems = list(csv.DictReader(io.StringIO((out / "problems.csv").read_text(encoding="utf-8-sig")), delimiter=";"))
    assert [(int(r["Linia CSV"]), r["Kolumna"]) for r in problems] == [(10, "value"), (14, "category")]
    from pypdf import PdfReader
    pdf = out / "weekly.pdf"
    reader = PdfReader(pdf)
    text = "\n".join(p.extract_text() for p in reader.pages)
    for token in ("1 250,00", "178,57", "2026-09-07", "2026-09-13", "PLN", "Nie potwierdzono", "550,00", "450,00", "250,00"):
        assert token in text, "PDF missing: " + token
    assert re.search(r"1 250,00\s+178,57\s+7(?:\s|$)", text), "PDF KPI table differs from independent reference"
    (out / "pdf-text.txt").write_text(text, encoding="utf-8")
    assert sha256(ROOT / "sample_data/pilot_demo.csv") == original_hash
    evidence = json.loads((out / "browser-evidence.json").read_text(encoding="utf-8"))
    evidence.update(date=args.date, input_kind="synthetic", runtime="Windows / Edge, local server",
                    mode="packaged-exe" if args.exe else "source", isolated_profiles=True,
                    pdf_pages=len(reader.pages), pdf_text_checks=True, diagnostic_csv_lines=[10, 14],
                    source_unchanged=True, expected=expected, pdf_sha256=sha256(pdf))
    if args.exe:
        evidence["exe_sha256"] = sha256(args.exe)
    if not args.verify_only:
        video = json.loads((out / "video.json").read_text(encoding="utf-8"))["path"]
        subprocess.run([str(args.ffmpeg.resolve()), "-y", "-i", video, "-an", "-c:v", "libx264",
                        "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                        str(media / "demo.mp4")], check=True, stdout=subprocess.DEVNULL,
                       stderr=(out / "encoder.log").open("w", encoding="utf-8"))
        probe = subprocess.run([str(args.ffmpeg.resolve()), "-i", str(media / "demo.mp4"), "-f", "null", "-"],
                               capture_output=True, text=True, encoding="utf-8", check=True)
        duration = re.search(r"Duration: (\d+):(\d+):([\d.]+)", probe.stderr)
        assert duration, "Video duration unavailable"
        evidence["video_duration_seconds"] = round(int(duration[1]) * 3600 + int(duration[2]) * 60 + float(duration[3]), 2)
        evidence["video_decode_passed"] = True
        destination = ROOT / "output/pdf/AutoReport-portfolio-demo-2026-10-04.pdf"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pdf, destination)
        shutil.copy2(pdf, portfolio / "demo-report.pdf")
        shutil.copy2(out / "bad.csv", portfolio / "bad-example.csv")
        shutil.copy2(out / "corrected.csv", portfolio / "corrected-example.csv")
        (portfolio / "expected.json").write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        evidence["media_sha256"] = {p.name: sha256(p) for p in sorted(media.iterdir()) if p.is_file()}
        (portfolio / "VERIFICATION.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(result="PASS", evidence=str(out / "evidence.json"), pdf_pages=len(reader.pages),
                          full_total=expected["full"]["total"], weekly_total=expected["current"]["total"])))


if __name__ == "__main__":
    main()
