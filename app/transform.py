"""Only validated records enter the reporting database."""
from contextlib import closing
from app.config import DB_PATH
from app.db import get_conn
from app.validation import CsvProfile, DataValidationError, inspect_records

DATE_COL = "date"
VALUE_COL = "value"
CATEGORY_COL = "category"


def write_facts(conn, rows):
    with conn:
        conn.execute("DROP TABLE IF EXISTS facts")
        conn.execute("CREATE TABLE facts (event_date TEXT NOT NULL, value_minor INTEGER NOT NULL, category TEXT NOT NULL)")
        conn.executemany("INSERT INTO facts VALUES (:event_date, :value_minor, :category)", rows)
        conn.execute("CREATE INDEX facts_date ON facts(event_date)")


def rebuild_facts():
    """Legacy adapter: validate before modifying any existing facts."""
    with closing(get_conn(DB_PATH)) as conn:
        raw = [dict(r) for r in conn.execute("SELECT * FROM facts_raw")]
        rows, quality = inspect_records(enumerate(raw, 2), CsvProfile(DATE_COL, VALUE_COL, CATEGORY_COL))
        if not raw or quality["invalid_rows"]:
            raise DataValidationError("Niepoprawne dane; poprzednie wyniki zachowane.", quality)
        write_facts(conn, rows)
