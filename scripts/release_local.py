"""One local command: pinned environment, regression, build, ZIP and EXE QA.

No publishing. Earlier releases are preserved. Choose a new tag per run.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def command(argv, logfile, env=None):
    print("Running " + Path(argv[-1]).name if len(argv)==2 else "Running: " + " ".join(str(x) for x in argv[1:4]), flush=True)
    with logfile.open("w", encoding="utf-8") as log:
        completed = subprocess.run([str(x) for x in argv], cwd=ROOT, env=env, stdout=log, stderr=log)
    if completed.returncode:
        raise RuntimeError(f"Step failed ({completed.returncode}); see {logfile}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-tag", required=True)
    parser.add_argument("--date", required=True, help="Client date YYYY-MM-DD")
    parser.add_argument("--python", type=Path, help="Already provisioned isolated Python, matching the lock")
    parser.add_argument("--benchmark-data", type=Path, help="Run real EXE on prepared benchmark CSVs")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9-]+", args.release_tag) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        parser.error("Invalid tag or date")
    log_dir = ROOT / "build/local-releases" / args.release_tag
    dist = ROOT / ("release/analyst-" + args.release_tag)
    archive = ROOT / ("release/AutoReportAnalyst-Windows-" + args.release_tag + ".zip")
    if dist.exists() or archive.exists() or log_dir.exists():
        parser.error("Tag already exists; choose a new tag. Earlier artifacts are preserved")
    log_dir.mkdir(parents=True)
    runtime = args.python.resolve() if args.python else log_dir / "venv/Scripts/python.exe"
    if not args.python:
        command([sys.executable, "-m", "venv", runtime.parents[1]], log_dir / "create-environment.log")
        command([runtime, "-m", "pip", "install", "-r", ROOT / "requirements-release-lock.txt"], log_dir / "install.log")
    installed = subprocess.check_output([runtime, "-m", "pip", "freeze"], text=True)
    pinned = (ROOT / "requirements-release-lock.txt").read_text(encoding="utf-8")
    normalize = lambda text: {line.strip().lower().replace('_', '-') for line in text.splitlines() if line.strip() and not line.startswith('#')}
    if normalize(installed) != normalize(pinned):
        raise RuntimeError("The isolated Python environment does not match requirements-release-lock.txt")
    (log_dir / "environment.txt").write_text(installed, encoding="utf-8")
    env = dict(os.environ, PYTHONIOENCODING="utf-8", AUTOREPORT_PROFILE_DIR=str(log_dir / "profiles"))
    command([runtime, "-m", "unittest", "discover", "-s", "tests", "-v"], log_dir / "regression.log", env)
    test_log = (log_dir / "regression.log").read_text(encoding="utf-8")
    count = re.search(r"Ran (\d+) tests", test_log)
    if not count or not test_log.rstrip().endswith("OK"):
        raise RuntimeError("No complete passing regression evidence")
    command([runtime, ROOT / "scripts/qa_interrupt_recovery.py"], log_dir / "interruption.log", env)
    command([runtime, ROOT / "scripts/build_analyst.py", "--release-tag", args.release_tag, "--skip-archive"], log_dir / "build.log", env)
    target = dist / "AutoReportAnalyst"
    # Entry instructions identify the actual tag; dated portfolio proof stays historical.
    for name in ("START_HERE.txt", "ANALYST_QUICKSTART.md"):
        path = target / name
        text = re.sub(r"AutoReportAnalyst-Windows-[a-zA-Z0-9-]+\.zip", archive.name, path.read_text(encoding="utf-8"))
        text = re.sub(r"(?<=WYDANIE )\d{4}-\d{2}-\d{2}", args.date, text)
        text = re.sub(r"(?<=Aktualizacja: )\d{4}-\d{2}-\d{2}", args.date, text)
        path.write_text(text, encoding="utf-8")
    for name in ("LOCAL_HARDENING_RESULTS.md", "LOCAL_HARDENING_EVIDENCE.json"):
        source = ROOT / "docs" / name
        if source.is_file():
            shutil.copy2(source, target / name)
    with (target / "README.md").open("a", encoding="utf-8") as f:
        f.write("\nBieżąca kontrola wydania: `RELEASE_CHECKS.json`. Protokół portfolio z 2026-10-04 i jego PDF/nagranie są wcześniejszymi przykładami.\n")
        if (target / "LOCAL_HARDENING_RESULTS.md").is_file():
            f.write("\n[Kontrole odporności z 2026-10-06](LOCAL_HARDENING_RESULTS.md). Dowody identyfikują sprawdzony EXE przez SHA-256.\n")
    sample_dir = ROOT / "output/pdf/local-hardening-2026-10-06"
    if sample_dir.is_dir():
        shutil.copytree(sample_dir, target / "pdf-edge-examples")
    manifest = dict(release=archive.name, date=args.date, source_rebuilt=True, application_version="0.2.0", template_version="4",
                    exe_sha256=digest(target / "AutoReportAnalyst.exe"), dependency_lock_sha256=digest(ROOT / "requirements-release-lock.txt"))
    (target / "RELEASE.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    candidate = log_dir / "candidate.zip"
    shutil.make_archive(str(candidate.with_suffix('')), "zip", dist, "AutoReportAnalyst")
    unpacked = log_dir / "unpacked"
    with ZipFile(candidate) as z:
        assert z.testzip() is None
        for name in z.namelist():
            assert (unpacked / name).resolve().is_relative_to(unpacked.resolve()), name
        z.extractall(unpacked)
    exe = unpacked / "AutoReportAnalyst/AutoReportAnalyst.exe"
    assert digest(exe) == manifest["exe_sha256"]
    command([runtime, ROOT / "scripts/verify_portfolio_links.py", "--package", unpacked / "AutoReportAnalyst"], log_dir / "links.log", env)
    sessions = set((ROOT / "build/portfolio").glob("session-*"))
    command([runtime, ROOT / "scripts/prepare_portfolio.py", "--verify-only", "--exe", exe, "--date", args.date], log_dir / "browser.log", env)
    created = set((ROOT / "build/portfolio").glob("session-*")) - sessions
    assert len(created) == 1
    ui = json.loads((created.pop() / "evidence.json").read_text(encoding="utf-8"))
    assert ui["exe_sha256"] == manifest["exe_sha256"]
    (log_dir / "browser-evidence.json").write_text(json.dumps(ui, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.benchmark_data:
        command([runtime, ROOT / "scripts/benchmark_local.py", "--out", args.benchmark_data, "--skip-source", "--exe", exe], log_dir / "benchmark.log", env)
    checks = dict(date=args.date, result="PASS", tests=int(count[1]), exe_sha256=manifest["exe_sha256"],
                  rebuilt_from_source=True, zip_crc_passed=True, browser_checks_passed=True,
                  pdf_snapshot_numbers_passed=True, dependency_lock_matched=True,
                  clean_windows="UNKNOWN", native_launcher="UNKNOWN")
    (target / "RELEASE_CHECKS.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    # Final ZIP changes only by adding verification metadata, not its runtime.
    shutil.make_archive(str(archive.with_suffix('')), "zip", dist, "AutoReportAnalyst")
    with ZipFile(archive) as z:
        assert z.testzip() is None
        assert hashlib.sha256(z.read("AutoReportAnalyst/AutoReportAnalyst.exe")).hexdigest() == manifest["exe_sha256"]
    checks.update(zip_sha256=digest(archive), zip_bytes=archive.stat().st_size, release=archive.name)
    (log_dir / "evidence.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print(json.dumps(checks), flush=True)


if __name__ == "__main__":
    main()
