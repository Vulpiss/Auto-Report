"""Build a separate portable dashboard; preserve the existing desktop release."""
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
command=[sys.executable,"-m","PyInstaller","--noconfirm","--onedir","--name","AutoReportDashboard",
         "--distpath",str(ROOT/"release/dashboard"),"--workpath",str(ROOT/"build/dashboard-package"),
         "--specpath",str(ROOT/"build"),"--collect-all","streamlit","--collect-all","altair",
         "--copy-metadata","streamlit","--hidden-import","app.analysis","--hidden-import","app.pipeline",
         "--hidden-import","app.pdf_report","--hidden-import","pandas","--hidden-import","altair",
         "--add-data",str(ROOT/"interfaces")+";interfaces",
         "--add-data",str(ROOT/"sample_data")+";sample_data",str(ROOT/"dashboard_entry.py")]
subprocess.run(command,cwd=ROOT,check=True)

import shutil
target=ROOT/"release/dashboard/AutoReportDashboard"
for source in ["docs/DASHBOARD_QUICKSTART.md","docs/DASHBOARD_PILOT.md","LICENSE"]:
    shutil.copy2(ROOT/source,target/Path(source).name)
shutil.make_archive(str(ROOT/"release/AutoReportDashboard-Windows"),"zip",ROOT/"release/dashboard","AutoReportDashboard")
