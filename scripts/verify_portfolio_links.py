"""Check local Markdown targets in current portfolio entry points."""
import argparse
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--package", type=Path)
args = parser.parse_args()
files = [ROOT / "README.md", ROOT / "docs/ANALYST_QUICKSTART.md", ROOT / "docs/LOCAL_HARDENING_RESULTS.md"] + list((ROOT / "docs/portfolio").glob("*.md"))
files += list((ROOT / "docs/first-test").glob("*.md"))
if args.package:
    files += [args.package / "README.md", args.package / "ANALYST_QUICKSTART.md"] + list((args.package / "portfolio").glob("*.md"))
    if (args.package / "LOCAL_HARDENING_RESULTS.md").is_file():
        files.append(args.package / "LOCAL_HARDENING_RESULTS.md")
count = 0
errors = []
for file in files:
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
        target = target.strip().strip("<>")
        if urlsplit(target).scheme or target.startswith("#"):
            continue
        destination = (file.parent / unquote(target.split("#", 1)[0])).resolve()
        count += 1
        if not destination.exists():
            errors.append(f"{file}: missing {target}")
if errors:
    raise SystemExit("\n".join(errors))
print(f"PASS: {count} local links in {len(files)} current documents")
