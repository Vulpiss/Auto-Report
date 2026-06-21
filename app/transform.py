from app.config import DB_PATH
from app.db import get_conn, execute

# 🔴 USTAW W UI!
DATE_COL = "date"
VALUE_COL = "value"
CATEGORY_COL = "category"

def rebuild_facts():
    conn = get_conn(DB_PATH)

    execute(conn, "DROP TABLE IF EXISTS facts;")

    query = f"""
    CREATE TABLE facts AS
    SELECT
        DATE({DATE_COL}) as event_date,
        CAST({VALUE_COL} as REAL) as value,
        {CATEGORY_COL} as category
    FROM facts_raw
    WHERE {DATE_COL} IS NOT NULL;
    """

    execute(conn, query)

    conn.close()