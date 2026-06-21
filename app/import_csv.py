import pandas as pd

from app.config import DB_PATH, INPUT_CSV_PATH
from app.db import get_conn


def import_csv_to_raw(csv_path: str | None = None):
    """
    Imports CSV into SQLite raw table.

    If csv_path is provided, it is used.
    Otherwise, config.INPUT_CSV_PATH is used.
    """
    source_path = csv_path or INPUT_CSV_PATH

    df = pd.read_csv(source_path)

    conn = get_conn(DB_PATH)
    df.to_sql("facts_raw", conn, if_exists="replace", index=False)
    conn.close()

    return df