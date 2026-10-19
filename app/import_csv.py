"""Compatibility import: validation precedes persistence; only canonical columns."""
from contextlib import closing
from app.config import DB_PATH, INPUT_CSV_PATH
from app.db import get_conn
from app.validation import load_csv, CsvProfile


def import_csv_to_raw(csv_path=None, profile=None):
    parsed = load_csv(csv_path or INPUT_CSV_PATH, profile or CsvProfile())
    # Kept for callers of the old API. The new pipeline uses in-memory facts directly.
    import pandas as pd
    df = pd.DataFrame([{"date": r["event_date"], "value": format(r["value_minor"] / 100, ".2f"), "category": r["category"]} for r in parsed.rows])
    with closing(get_conn(DB_PATH)) as conn:
        df.to_sql("facts_raw", conn, if_exists="replace", index=False)
    return df
