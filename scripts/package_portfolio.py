"""Assemble portfolio materials around a previously verified Windows runtime.

Preserves earlier releases. Does not compile, publish or replace the source EXE.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def copy_materials(target, zip_name):
    sources = ["docs/START_HERE.txt", "docs/ANALYST_QUICKSTART.md", "docs/DATA_DIAGNOSTICS.md",
               "docs/DATA_CONTRACT.md", "sample_data/wholesale_business.csv",
               "sample_data/wholesale_business.profile.json", "LICENSE"]
    for source in sources:
        shutil.copy2(ROOT / source, target / Path(source).name)
    shutil.copytree(ROOT / "docs/portfolio", target / "portfolio", dirs_exist_ok=True)
    template = (ROOT / "docs/PORTFOLIO_PACKAGE_README.md").read_text(encoding="utf-8")
    (target / "README.md").write_text(template.replace("{{RELEASE_ZIP}}", zip_name), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", required=True, type=Path, help="Directory with verified EXE and _internal")
    parser.add_argument("--release-tag", default="2026-10-04-portfolio")
    parser.add_argument("--refresh-materials", action="store_true", help="Refresh docs and ZIP of this portfolio release")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9-]+", args.release_tag):
        parser.error("release-tag: letters, digits and hyphens only")
    runtime = args.runtime.resolve()
    if not (runtime / "AutoReportAnalyst.exe").is_file() or not (runtime / "_internal").is_dir():
        parser.error("Runtime must contain AutoReportAnalyst.exe and _internal")
    dist = ROOT / ("release/analyst-" + args.release_tag)
    target = dist / "AutoReportAnalyst"
    archive = ROOT / ("release/AutoReportAnalyst-Windows-" + args.release_tag + ".zip")
    if target.exists() and not args.refresh_materials:
        parser.error("Release exists; choose a new tag or explicitly refresh its materials")
    if target.exists():
        assert digest(runtime / "AutoReportAnalyst.exe") == digest(target / "AutoReportAnalyst.exe"), "Refresh cannot change EXE"
    else:
        target.mkdir(parents=True)
        shutil.copy2(runtime / "AutoReportAnalyst.exe", target / "AutoReportAnalyst.exe")
        shutil.copytree(runtime / "_internal", target / "_internal")
    copy_materials(target, archive.name)
    manifest = dict(release=archive.name, application_version="0.2.0", date="2026-10-04",
                    runtime_origin=runtime.parent.name, source_rebuilt=False,
                    exe_sha256=digest(target / "AutoReportAnalyst.exe"),
                    note="Unchanged verified runtime; updated portfolio materials.",
                    portfolio_files={str(p.relative_to(target)).replace('\\', '/'): digest(p)
                                     for p in sorted((target / "portfolio").rglob('*')) if p.is_file()})
    (target / "RELEASE.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.make_archive(str(archive.with_suffix('')), "zip", dist, "AutoReportAnalyst")
    with ZipFile(archive) as z:
        assert z.testzip() is None, "Archive CRC failed"
        assert hashlib.sha256(z.read("AutoReportAnalyst/AutoReportAnalyst.exe")).hexdigest() == manifest["exe_sha256"]
        for file, expected in manifest["portfolio_files"].items():
            assert hashlib.sha256(z.read("AutoReportAnalyst/" + file)).hexdigest() == expected, file
    evidence = dict(release=archive.name, bytes=archive.stat().st_size, zip_sha256=digest(archive),
                    exe_sha256=manifest["exe_sha256"], crc_passed=True, portfolio_hashes_passed=True)
    destination = ROOT / "build/portfolio/package-evidence.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence))


if __name__ == "__main__":
    main()
