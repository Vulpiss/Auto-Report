import os
import sys


def get_base_dir() -> str:
    """
    Returns project/application base directory.

    Normal Python mode:
        Auto-Report/

    PyInstaller .exe mode:
        folder where AutoReport.exe is located
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    # __file__ = Auto-Report/app/config.py
    # app_dir = Auto-Report/app
    # project_dir = Auto-Report
    app_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(app_dir)

    return project_dir


BASE_DIR = get_base_dir()

# -------------------------
# Main paths
# -------------------------
DB_PATH = os.path.join(BASE_DIR, "report.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Default CSV path used when running from main.py without GUI.
# In desktop_app.py the user selects CSV manually, so this is only fallback.
INPUT_CSV_PATH = os.path.join(BASE_DIR, "sample_data", "input_with_baseline.csv")

# -------------------------
# LLM settings
# -------------------------
USE_LLM = False

# -------------------------
# Reporting settings
# -------------------------
REPORT_LAST_N_DAYS = 60