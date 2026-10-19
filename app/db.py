import sqlite3

def get_conn(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def execute(conn, query, params=None):
    cur = conn.cursor()
    cur.execute(query, params or [])
    conn.commit()


def fetch_all(conn, query, params=None):
    cur = conn.cursor()
    cur.execute(query, params or [])
    return cur.fetchall()