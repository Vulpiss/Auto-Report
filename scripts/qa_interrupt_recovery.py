"""Terminate only owned test children during import/export, then verify recovery."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
RAW = b"date,value,category\n2026-10-06,12.34,A\n"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--worker", choices=["import", "export"])
parser.add_argument("--root", type=Path)
args = parser.parse_args()
if args.worker:
    marker = args.root / "ready"
    if args.worker == "import":
        from app.validation import load_csv
        def progress(count):
            if count >= 10000:
                marker.write_text("Import reached 10000 rows", encoding="utf-8")
                time.sleep(30)
        load_csv(args.root / "input.csv", progress=progress)
    else:
        import app.pipeline as pipeline
        def paused_chart(data, path, **kwargs):
            Path(path).write_bytes(b"Partial chart; never a completed report")
            marker.write_text("Export staging reached", encoding="utf-8")
            time.sleep(30)
        pipeline.plot_trend = paused_chart
        pipeline.generate_report(RAW, output_dir=args.root / "reports")
    raise SystemExit(0)

from app.pipeline import generate_report
out = ROOT / "build/local-hardening" / ("interrupt-" + uuid4().hex[:10])
out.mkdir(parents=True)
results = []
for mode in ("import", "export"):
    test = out / mode
    test.mkdir()
    source = test / "input.csv"
    source.write_bytes(b"date,value,category\n" + b"2026-10-06,0.01,A\n" * 100000)
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    first = Path(generate_report(RAW, output_dir=test / "reports"))
    previous = first.read_bytes()
    env = dict(os.environ, AUTOREPORT_PROFILE_DIR=str(test / "profiles"))
    with (test / "child.log").open("w", encoding="utf-8") as log:
        child = subprocess.Popen([sys.executable, str(Path(__file__)), "--worker", mode, "--root", str(test)], cwd=ROOT, env=env, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        try:
            deadline = time.monotonic()+20
            while not (test / "ready").exists():
                if child.poll() is not None:
                    raise RuntimeError("Interrupted test child exited before reaching stage")
                if time.monotonic()>deadline:
                    raise TimeoutError("Child did not reach the intended interruption point")
                time.sleep(.05)
            child.terminate()
            child.wait(timeout=5)
        finally:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=5)
    assert first.read_bytes() == previous
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    published = [p for p in (test / "reports").iterdir() if not p.name.startswith(".pending-")]
    assert published == [first.parent]
    retry = Path(generate_report(RAW, output_dir=test / "reports"))
    summary = json.loads((retry.parent / "summary.json").read_text(encoding="utf-8"))
    assert summary["kpis"]["total_minor"] == 1234
    assert retry.read_bytes().startswith(b"%PDF")
    results.append(dict(stage=mode, child_terminated=True, previous_report_unchanged=True,
                        source_unchanged=True, no_partial_report_published=True, retry_minor=1234))
evidence = dict(date="2026-10-06", synthetic=True, result="PASS", cases=results,
                scope="Only owned children terminated; temporary unfinished exports kept separately for diagnostics")
(out / "evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
print(json.dumps(dict(result="PASS", evidence=str(out / "evidence.json"))))
