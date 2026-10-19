"""Build a separate portable dashboard; preserve the existing desktop release."""
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
import argparse,re
parser=argparse.ArgumentParser()
parser.add_argument("--release-tag",default="")
parser.add_argument("--skip-archive",action="store_true",help="Build the directory; the verified release pipeline creates the ZIP")
args=parser.parse_args()
if args.release_tag and not re.fullmatch(r"[a-zA-Z0-9-]+",args.release_tag):
    parser.error("release-tag: użyj liter, cyfr i myślników")
suffix="-"+args.release_tag if args.release_tag else ""
dist=ROOT/("release/analyst"+suffix)
command=[sys.executable,"-m","PyInstaller","--noconfirm","--onedir","--windowed","--name","AutoReportAnalyst",
         "--distpath",str(dist),"--workpath",str(ROOT/"build/analyst-package"),
         "--specpath",str(ROOT/"build"),"--collect-all","streamlit","--collect-all","altair",
         "--copy-metadata","streamlit","--hidden-import","app.profile_library","--hidden-import","app.simple_import","--hidden-import","app.analysis","--hidden-import","app.analyst_tools","--hidden-import","app.business","--hidden-import","app.workspace","--hidden-import","app.editable_presentation","--hidden-import","app.pipeline",
         "--hidden-import","app.presentation","--hidden-import","app.dashboard_model","--hidden-import","app.dashboard_render","--hidden-import","interfaces.dashboard_views","--hidden-import","interfaces.import_feedback","--hidden-import","app.pdf_report","--hidden-import","pandas","--hidden-import","altair",
         "--add-data",str(ROOT/"assets")+";assets","--add-data",str(ROOT/"interfaces")+";interfaces",
         "--add-data",str(ROOT/"sample_data")+";sample_data",str(ROOT/"dashboard_entry.py")]
subprocess.run(command,cwd=ROOT,check=True)

import shutil
target=dist/"AutoReportAnalyst"
shutil.copy2(ROOT/"docs/SIMPLE_MODE_RESULTS.md",target/"SIMPLE_MODE_RESULTS.md")
shutil.copy2(ROOT/"docs/ONECLICK_RESULTS.md",target/"ONECLICK_RESULTS.md")
shutil.copy2(ROOT/"docs/DATA_DIAGNOSTICS.md",target/"DATA_DIAGNOSTICS.md")
shutil.copy2(ROOT/"docs/DATA_CONTRACT.md",target/"DATA_CONTRACT.md")
for source in ["docs/START_HERE.txt","docs/SELF_TEST.md","docs/SELF_TEST_OBSERVATIONS.csv","docs/INTERNAL_ACCEPTANCE_RESULTS.md","docs/DASHBOARD_POLISH_RESULTS.md","docs/ANALYST_TASK_TEST.md","docs/analyst_task_observations.csv","sample_data/wholesale_business.csv","sample_data/wholesale_business.profile.json","docs/ANALYST_UPGRADE.md","docs/KAGGLE_SUPERSTORE_TEST.md","docs/ANALYST_QUICKSTART.md","docs/DASHBOARD_PILOT.md","docs/ANALYST_ACCEPTANCE.md","docs/pilot_cycles.csv","scripts/Test-AnalystWindows.ps1","LICENSE"]:
    shutil.copy2(ROOT/source,target/Path(source).name)
shutil.copytree(ROOT/"sample_data/internal_acceptance",target/"internal_acceptance",dirs_exist_ok=True)
if (ROOT/"docs/portfolio/VERIFICATION.md").is_file():
    shutil.copytree(ROOT/"docs/portfolio",target/"portfolio",dirs_exist_ok=True)
    template=(ROOT/"docs/PORTFOLIO_PACKAGE_README.md").read_text(encoding="utf-8")
    (target/"README.md").write_text(template.replace("{{RELEASE_ZIP}}","AutoReportAnalyst-Windows"+suffix+".zip"),encoding="utf-8")
if not args.skip_archive:
    shutil.make_archive(str(ROOT/("release/AutoReportAnalyst-Windows"+suffix)),"zip",dist,"AutoReportAnalyst")
