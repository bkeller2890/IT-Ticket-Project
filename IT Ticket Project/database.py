import sqlite3
from contextlib import contextmanager

from flask import g


# -------------------------
# DB Connection / Setup
# -------------------------
def get_connection(db_name="tickets.db"):
    conn = sqlite3.connect(db_name, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def setup_db(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()


def get_db():
    if "db" not in g:
        g.db = get_connection()
        setup_db(g.db)
    return g.db


@contextmanager
def db_session():
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def close_db(error):
    db = g.pop("db", None)
    if db:
        db.close()


# -------------------------
# App constants
# -------------------------
PRIORITIES = ["Low", "Medium", "High"]
STATUSES = ["Open", "In Progress", "Closed"]
