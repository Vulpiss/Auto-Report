import io,json,sys,time
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from streamlit.testing.v1 import AppTest
out=Path("build/full-kaggle-qa");out.mkdir(exist_ok=True)
raw=Path("data/external/kaggle-large/data.csv").read_bytes()
with patch("streamlit.file_uploader",return_value=io.BytesIO(raw)):
 app=AppTest.from_file("interfaces/streamlit_app.py",default_timeout=180).run()
 app.button(key="retail_profile").click().run()
 t=time.perf_counter();app.button(key="load").click().run();load=time.perf_counter()-t
 assert not app.exception and not app.error, str(app.error)
 assert len(app.session_state["parsed"].rows)==541909
 timings={}
 for view in app.radio(key="view").options:
  t=time.perf_counter();app.radio(key="view").set_value(view).run()
  assert not app.exception and not app.error,str(app.error)
  timings[view]=time.perf_counter()-t
 with patch("app.pipeline.OUTPUT_DIR",out/"ui-pdf"):
  app.button(key="export").click().run()
  assert not app.exception and not app.error,str(app.error)
 (out/"ui-evidence.json").write_text(json.dumps(dict(rows=541909,load_ui_s=load,view_s=timings,pdf=True,scope="Streamlit AppTest, default final seven days, not browser or EXE"),ensure_ascii=False,indent=2),encoding="utf-8")
print("UI PASS")
