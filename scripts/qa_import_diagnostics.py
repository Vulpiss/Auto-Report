"""Check repair locations and CSV download in an isolated local browser session."""
import argparse
import csv
import io
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--exe", type=Path)
args = parser.parse_args()
out = ROOT / "build" / ("import-diagnostics-exe-qa" if args.exe else "import-diagnostics-source-qa")
out.mkdir(parents=True, exist_ok=True)
(out / "bad.csv").write_text("date,value,category\n" + "2026-10-01,abc,\n" * 75, encoding="utf-8")
(out / "corrected.csv").write_text("date,value,category\n2026-10-01,10,A\n2026-10-02,20,A\n2026-10-03,30,B\n", encoding="utf-8")
with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
env = dict(os.environ, AUTOREPORT_PROFILE_DIR=str(out / ("profiles-" + uuid4().hex)), PYTHONDONTWRITEBYTECODE="1")
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
                raise RuntimeError("Local QA server stopped; see server.log")
            try:
                with urllib.request.urlopen(url + "/_stcore/health", timeout=1) as response:
                    if response.status == 200:
                        break
            except OSError:
                if time.monotonic() > deadline:
                    raise TimeoutError("Local QA server did not start")
                time.sleep(.25)
        node = shutil.which("node")
        if not node:
            raise RuntimeError("Node runtime unavailable for browser QA")
        subprocess.run([node, str(ROOT / "scripts/qa_import_diagnostics.cjs"), url, str(out)],
                       cwd=ROOT, env=env, check=True, timeout=120)
        records = list(csv.DictReader(io.StringIO((out / "problems.csv").read_text(encoding="utf-8-sig")), delimiter=";"))
        assert len(records) == 150, len(records)
        assert records[-1]["Linia CSV"] == "76"
        assert records[-1]["Kolumna"] == "category"
        evidence = json.loads((out / "browser-evidence.json").read_text(encoding="utf-8"))
        evidence.update(csv_problems=len(records), last_csv_line=76)
        (out / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(evidence, ensure_ascii=False))
    finally:
        child.terminate()
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=10)
