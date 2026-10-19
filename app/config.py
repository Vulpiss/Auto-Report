import os
from pathlib import Path
import sys

VERSION = "0.2.0"
BASE_DIR = str(Path(__file__).resolve().parents[1])
DATA_DIR = Path(os.environ.get("AUTOREPORT_HOME", str(Path(os.environ.get("LOCALAPPDATA", Path.home())) / "AutoReport")))
OUTPUT_DIR = str(DATA_DIR / "reports")
DB_PATH = str(DATA_DIR / "legacy-report.db")
INPUT_CSV_PATH = str(Path(BASE_DIR) / "sample_data" / "input_with_baseline.csv")
USE_LLM = False
REPORT_LAST_N_DAYS = 7


def get_base_dir():
    return BASE_DIR
