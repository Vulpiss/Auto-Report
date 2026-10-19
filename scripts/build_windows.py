"""Build the isolated 0.2.0 portable package; never overwrite the old dist/."""
from pathlib import Path
import os
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    if sys.platform != "win32":
        raise SystemExit("Build requires Windows.")
    import PyInstaller.__main__
    os.chdir(ROOT)
    release = ROOT / "release" / "v0.2.0"
    PyInstaller.__main__.run([
        "--noconfirm", "--onedir", "--windowed", "--name", "AutoReport",
        "--distpath", str(release), "--workpath", str(ROOT / "build" / "v0.2.0"),
        "--specpath", str(ROOT / "build" / "v0.2.0"),
        "--paths", str(ROOT),
        "--add-data", str(ROOT / "sample_data" / "pilot_demo.csv") + ";sample_data",
        "--collect-data", "matplotlib",
        "--exclude-module", "streamlit", "--exclude-module", "pandas",
        "--exclude-module", "IPython", "--exclude-module", "tkinter.test",
        str(ROOT / "interfaces" / "desktop_app.py"),
    ])
    target = release / "AutoReport"
    shutil.copy2(ROOT / "docs" / "QUICKSTART_PL.md", target / "START_TUTAJ.md")
    shutil.copy2(ROOT / "sample_data" / "pilot_demo.csv", target / "PRZYKLAD.csv")
    shutil.copy2(ROOT / "LICENSE", target / "LICENSE")
    print(target / "AutoReport.exe")


if __name__ == "__main__":
    main()
