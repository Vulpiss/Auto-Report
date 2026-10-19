"""Synthetic CSV boundaries and isolated measurements of the current app.

Source runs use fresh processes. EXE runs measure the actual browser import,
analysis and automatic PDF combined, excluding file selection by a person.
"""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from datetime import date, timedelta
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def peak_memory(pid):
    if os.name != "nt":
        return None
    from ctypes import wintypes as W
    class Counters(ctypes.Structure):
        _fields_ = [("cb", W.DWORD), ("PageFaultCount", W.DWORD)] + [(n, ctypes.c_size_t) for n in
            ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage", "PrivateUsage")]
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel.OpenProcess.argtypes, kernel.OpenProcess.restype = [W.DWORD, W.BOOL, W.DWORD], W.HANDLE
    kernel.CloseHandle.argtypes = [W.HANDLE]
    psapi.GetProcessMemoryInfo.argtypes = [W.HANDLE, ctypes.POINTER(Counters), W.DWORD]
    handle = kernel.OpenProcess(0x410, False, pid)
    if not handle:
        return None
    try:
        info = Counters()
        info.cb = ctypes.sizeof(info)
        if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(info), info.cb):
            return None
        return dict(peak_working_set_mib=round(info.PeakWorkingSetSize/1024**2, 2),
                    peak_private_commit_mib=round(info.PeakPagefileUsage/1024**2, 2))
    finally:
        kernel.CloseHandle(handle)


def prepare(out):
    out.mkdir(parents=True)
    specs = [dict(name="100k", rows=100000, categories=500, days=14, start="2026-09-23", end="2026-10-06"),
             dict(name="1m-5lat", rows=1000000, categories=2000, days=1826, start="2021-10-07", end="2026-10-06")]
    for spec in specs:
        origin = date.fromisoformat(spec["start"])
        dates = [str(origin + timedelta(days=i)) for i in range(spec["days"])]
        assert dates[-1] == spec["end"]
        labels = [f"K{i:04} Żółć " + "wyposażenie " * 4 for i in range(spec["categories"])]
        path = out / (spec["name"] + ".csv")
        with path.open("w", encoding="utf-8", newline="") as f:
            f.write("date,value,category\n")
            for i in range(spec["rows"]):
                f.write(f"{dates[i%spec['days']]},1.01,{labels[i%spec['categories']]}\n")
        spec.update(bytes=path.stat().st_size, expected_minor=101*spec["rows"], average="1.01")
        assert spec["bytes"] <= 100*1024**2
    shutil.copyfile(out / "1m-5lat.csv", out / "over-rows.csv")
    with (out / "over-rows.csv").open("ab") as f:
        f.write(b"2026-10-06,1.01,Extra\n")
    with (out / "over-bytes.csv").open("wb") as f:
        f.seek(100*1024**2)
        f.write(b"\n")
    (out / "specs.json").write_text(json.dumps(specs, ensure_ascii=False, indent=2), encoding="utf-8")
    return specs


def worker(out, name):
    from app.analysis import analyze
    from app.dashboard_model import make_model, table_page
    from app.validation import load_csv, DataValidationError
    if name in ("over-rows", "over-bytes"):
        start = time.perf_counter()
        try:
            load_csv(out / (name + ".csv"))
        except DataValidationError as exc:
            expected = "1000000" if name == "over-rows" else "100 MiB"
            assert expected in str(exc), str(exc)
            return dict(case=name, result="REJECTED", seconds=round(time.perf_counter()-start, 3), memory=peak_memory(os.getpid()))
        raise AssertionError("Import beyond the limit accepted")
    spec = next(s for s in json.loads((out / "specs.json").read_text(encoding="utf-8")) if s["name"] == name)
    begin = time.perf_counter()
    result = analyze(out / (name + ".csv"), start_date=spec["start"], end_date=spec["end"])
    analysis_s = time.perf_counter()-begin
    assert result["kpis"]["total_minor"] == spec["expected_minor"]
    assert result["kpis"]["rows_cnt"] == spec["rows"]
    assert str(result["kpis"]["avg_value"]) == spec["average"]
    begin = time.perf_counter()
    model = make_model(result)
    page = table_page(result, model)
    assert sum(int(r["value"]*100) for r in model["structure"] if r["value"] is not None) == spec["expected_minor"]
    return dict(case=name, result="PASS", rows=spec["rows"], bytes=spec["bytes"], expected_minor=spec["expected_minor"],
                analysis_seconds=round(analysis_s, 3), model_and_page_seconds=round(time.perf_counter()-begin, 3), visible_rows=len(page), memory=peak_memory(os.getpid()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--worker")
    parser.add_argument("--exe", type=Path)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--skip-source", action="store_true")
    parser.add_argument("--source-cases", nargs="+", help="Run selected source cases and preserve previous measurements")
    args = parser.parse_args()
    out = args.out or ROOT / "build/local-hardening" / ("benchmark-" + uuid4().hex[:10])
    if args.worker:
        print(json.dumps(worker(out, args.worker)))
        return
    specs = json.loads((out / "specs.json").read_text(encoding="utf-8")) if (out / "specs.json").is_file() else prepare(out)
    if args.prepare_only:
        print(json.dumps(dict(out=str(out), cases=specs)))
        return
    saved_source = out / "source-evidence.json"
    previous = json.loads(saved_source.read_text(encoding="utf-8")) if saved_source.exists() else []
    evidence = dict(date="2026-10-06", platform=platform.platform(), python=platform.python_version(), synthetic=True, specs=specs, source=previous)
    env = dict(os.environ, AUTOREPORT_PROFILE_DIR=str(out / "profiles"), PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    if not args.skip_source:
        for name in args.source_cases or ([s["name"] for s in specs] + ["over-rows", "over-bytes"]):
            run = subprocess.run([sys.executable, str(Path(__file__)), "--out", str(out), "--worker", name], check=True, capture_output=True, text=True, encoding="utf-8", timeout=180, env=env)
            evidence["source"] = [r for r in evidence["source"] if r["case"] != name]
            evidence["source"].append(json.loads(run.stdout))
            saved_source.write_text(json.dumps(evidence["source"], indent=2), encoding="utf-8")
            print(json.dumps(evidence["source"][-1]), flush=True)
    if args.exe:
        os.environ["AUTOREPORT_PROFILE_DIR"] = env["AUTOREPORT_PROFILE_DIR"]
        from app.profile_library import remember
        from app.validation import CsvProfile
        remember(["date", "value", "category"], CsvProfile())
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        url = f"http://127.0.0.1:{port}"
        with (out / "exe-server.log").open("w", encoding="utf-8") as log:
            child = subprocess.Popen([str(args.exe.resolve()), "--serve", str(port), "--log", str(out / "exe.log")], env=env, cwd=ROOT, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            sampled, stopped = [], threading.Event()
            def monitor():
                while not stopped.wait(.2):
                    value = peak_memory(child.pid)
                    if value:
                        sampled.append(value)
            monitor_thread = threading.Thread(target=monitor, daemon=True)
            monitor_thread.start()
            try:
                until = time.monotonic()+60
                while True:
                    if child.poll() is not None:
                        raise RuntimeError("EXE server exited")
                    try:
                        urllib.request.urlopen(url+"/_stcore/health", timeout=1).close()
                        break
                    except OSError:
                        if time.monotonic()>until:
                            raise TimeoutError("EXE health timeout")
                        time.sleep(.25)
                subprocess.run([shutil.which("node"), str(ROOT / "scripts/qa_large_local.cjs"), url, str(out)], check=True, cwd=ROOT, env=env, timeout=360)
                evidence["exe"] = json.loads((out / "exe-browser.json").read_text(encoding="utf-8"))
                evidence["exe_sha256"] = hashlib.sha256(args.exe.read_bytes()).hexdigest()
            finally:
                stopped.set()
                monitor_thread.join(timeout=2)
                child.terminate()
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=10)
            evidence["exe_memory"] = {k:max(v[k] for v in sampled) for k in sampled[0]} if sampled else None
    evidence["scope"] = "Local synthetic data; one run per case. Process memory excludes browser/OS. No guarantee for arbitrary computers or exports."
    (out / "evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(dict(result="PASS", evidence=str(out / "evidence.json"))))


if __name__ == "__main__":
    main()
