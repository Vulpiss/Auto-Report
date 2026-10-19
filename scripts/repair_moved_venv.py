"""Repair installed Windows entry-point launchers after moving this project's venv."""
from pathlib import Path
import sys,shutil,json
from datetime import datetime
from importlib.metadata import distributions
from pip._vendor.distlib.scripts import ScriptMaker
root=Path(__file__).resolve().parents[1]
venv=root/"venv"
if Path(sys.prefix).resolve()!=venv.resolve():
    raise SystemExit("Run with this project's venv/Scripts/python.exe")
scripts=venv/"Scripts"
backup=root/"build"/("venv-relocation-backup-"+datetime.now().strftime("%Y%m%d-%H%M%S"))
backup.mkdir(parents=True,exist_ok=False)
for path in scripts.iterdir():
    if path.is_file() and (path.suffix.lower()==".exe" or path.name.startswith("activate")):
        shutil.copy2(path,backup/path.name)
maker=ScriptMaker(None,str(scripts))
maker.executable=str(scripts/"python.exe")
maker.clobber=True
maker.variants={""}
generated=[]
for dist in distributions():
    for ep in dist.entry_points:
        if ep.group not in ("console_scripts","gui_scripts"):continue
        if Path(ep.name).name!=ep.name:raise ValueError("Invalid entry point name")
        generated.extend(maker.make(f"{ep.name} = {ep.value}",options={"gui":ep.group=="gui_scripts"}))
# pip's generated version-specific wrappers are not separate package entry points.
for name in ("pip3",f"pip{sys.version_info.major}.{sys.version_info.minor}"):
    generated.extend(maker.make(f"{name} = pip._internal.cli.main:main"))
for path in scripts.glob("activate*"):
    if path.suffix==".exe":continue
    text=path.read_text(encoding="utf-8")
    import re
    text=re.sub(r"C:\\Users\\kompu\\Desktop\\python kurs\\Auto-Report(?:-v2)?\\venv",lambda _:str(venv),text)
    path.write_text(text,encoding="utf-8")
(backup/"manifest.json").write_text(json.dumps({"python":sys.executable,"generated":generated},indent=2),encoding="utf-8")
print(f"Regenerated {len(generated)} launchers. Backup: {backup}")
