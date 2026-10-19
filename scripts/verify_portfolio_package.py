"""Unpack a generated ZIP separately and check its EXE through the browser."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from uuid import uuid4
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--zip", required=True, type=Path)
args = parser.parse_args()
destination = ROOT / "build/portfolio" / ("unpacked-" + uuid4().hex[:10])
with ZipFile(args.zip) as z:
    assert z.testzip() is None
    # Only accept paths confined to this fresh workspace directory.
    for name in z.namelist():
        assert (destination / name).resolve().is_relative_to(destination.resolve()), name
    z.extractall(destination)
package = destination / "AutoReportAnalyst"
manifest = json.loads((package / "RELEASE.json").read_text(encoding="utf-8"))
exe = package / "AutoReportAnalyst.exe"
exe_hash = hashlib.sha256(exe.read_bytes()).hexdigest()
assert exe_hash == manifest["exe_sha256"]
subprocess.run([sys.executable, str(ROOT / "scripts/verify_portfolio_links.py"), "--package", str(package)], check=True, cwd=ROOT)
existing = set((ROOT / "build/portfolio").glob("session-*"))
subprocess.run([sys.executable, str(ROOT / "scripts/prepare_portfolio.py"), "--verify-only", "--exe", str(exe)], check=True, cwd=ROOT)
created = set((ROOT / "build/portfolio").glob("session-*")) - existing
assert len(created) == 1
session = created.pop()
evidence = json.loads((session / "evidence.json").read_text(encoding="utf-8"))
assert evidence["exe_sha256"] == exe_hash
result = dict(date="2026-10-04", package=args.zip.name, crc_passed=True,
              exe_from_zip_sha256=exe_hash, ui_checks=evidence,
              limit="Local Windows / Edge server test; no clean Windows or native launcher test")
# Runtime checks remain applicable after a documentation-only archive refresh.
# The final ZIP checksum is written by package_portfolio.py outside the ZIP.
(ROOT / "docs/portfolio/PACKAGE_VERIFICATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(dict(result="PASS", package=args.zip.name, tested_exe=exe_hash)))
