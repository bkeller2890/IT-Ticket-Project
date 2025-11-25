import sqlite3
from datetime import datetime

# -------------------------
# Database Setup
# -------------------------
def get_connection(db_name="tickets.db"):
    return sqlite3.connect(db_name, check_same_thread=False)

def setup_db(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()

# -------------------------
# Database Functions
# -------------------------
def create_ticket_db(title, description, priority, status, created_at, updated_at, conn):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tickets (title, description, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, description, priority, status, created_at, updated_at))
    conn.commit()
    return cursor.lastrowid

def view_tickets_db(conn, filter_status=None, sort_by=None, search_keyword=None, page=1, per_page=10):
    cursor = conn.cursor()
    query = "SELECT * FROM tickets"
    filters = []
    params = []

    if filter_status:
        filters.append("status = ?")
        params.append(filter_status)

    if search_keyword:
        filters.append("(title LIKE ? OR description LIKE ?)")
        params.extend([f"%{search_keyword}%", f"%{search_keyword}%"])

    if filters:
        query += " WHERE " + " AND ".join(filters)

    # Sorting
    if sort_by == "priority":
        query += """ ORDER BY CASE UPPER(priority)
                        WHEN 'HIGH' THEN 1
                        WHEN 'MEDIUM' THEN 2
                        WHEN 'LOW' THEN 3
                    END"""
    elif sort_by == "date":
        query += " ORDER BY created_at ASC"
    else:
        query += " ORDER BY id ASC"

    # Pagination
    offset = (page - 1) * per_page
    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    cursor.execute(query, params)
    return cursor.fetchall()

def get_ticket_count(conn, filter_status=None, search_keyword=None):
    cursor = conn.cursor()
    query = "SELECT COUNT(*) FROM tickets"
    filters = []
    params = []

    if filter_status:
        filters.append("status = ?")
        params.append(filter_status)

    if search_keyword:
        filters.append("(title LIKE ? OR description LIKE ?)")
        params.extend([f"%{search_keyword}%", f"%{search_keyword}%"])

    if filters:
        query += " WHERE " + " AND ".join(filters)

    cursor.execute(query, params)
    return cursor.fetchone()[0]

def update_ticket_db(ticket_id, title=None, description=None, priority=None, status=None, conn=None):
    cursor = conn.cursor()
    # use explicit whitelist for columns to avoid constructing SQL from untrusted input
    VALID_UPDATE_COLUMNS = {"title", "description", "priority", "status", "updated_at"}
    cols = []
    params = []

    if title is not None:
        cols.append(("title", title))
    if description is not None:
        cols.append(("description", description))
    if priority is not None:
        cols.append(("priority", priority))
    if status is not None:
        cols.append(("status", status))

    if not cols:
        return 0  # nothing to update

    # always update timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cols.append(("updated_at", now))

    total_rows = 0
    for col, val in cols:
        if col not in VALID_UPDATE_COLUMNS:
            raise ValueError(f"Invalid column for update: {col}")
        if col == "title":
            total_rows += cursor.execute(
                "UPDATE tickets SET title = ?, updated_at = ? WHERE id = ?",
                (val, now, ticket_id),
            ).rowcount
        elif col == "description":
            total_rows += cursor.execute(
                "UPDATE tickets SET description = ?, updated_at = ? WHERE id = ?",
                (val, now, ticket_id),
            ).rowcount
        elif col == "priority":
            total_rows += cursor.execute(
                "UPDATE tickets SET priority = ?, updated_at = ? WHERE id = ?",
                (val, now, ticket_id),
            ).rowcount
        elif col == "status":
            total_rows += cursor.execute(
                "UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?",
                (val, now, ticket_id),
            ).rowcount

    conn.commit()
    return total_rows

def delete_ticket_db(ticket_id, conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tickets WHERE id=?", (ticket_id,))
    conn.commit()
    return cursor.rowcount

# -------------------------
# Logic Functions (Flask-ready)
# -------------------------
def create_ticket_logic(title, description, priority, conn):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return create_ticket_db(title, description, priority, "Open", now, now, conn)

def get_tickets_logic(conn, filter_status=None, sort_by=None, search_keyword=None, page=1, per_page=10):
    return view_tickets_db(conn, filter_status, sort_by, search_keyword, page, per_page)

def get_ticket_count_logic(conn, filter_status=None, search_keyword=None):
    return get_ticket_count(conn, filter_status, search_keyword)

def update_ticket_status_logic(ticket_id, title=None, description=None, priority=None, status=None, conn=None):
    return update_ticket_db(ticket_id, title=title, description=description, priority=priority, status=status, conn=conn)

def delete_ticket_logic(ticket_id, conn):
    return delete_ticket_db(ticket_id, conn)
