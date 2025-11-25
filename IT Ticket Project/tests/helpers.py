import sqlite3
from datetime import datetime

VALID_UPDATE_COLUMNS = {"title", "description", "priority", "status", "updated_at"}


def get_connection(path=":memory:"):
    conn = sqlite3.connect(path)
    return conn


def setup_db(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()


def _create_ticket_db(title, description, priority, status, created_at, updated_at, conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tickets (title, description, priority, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (title, description, priority, status, created_at, updated_at),
    )
    conn.commit()
    return cursor.lastrowid


def create_ticket_db(title, description, priority, *args):
    # Compatibility wrapper preserved for tests
    # Legacy call: create_ticket_db(title, description, priority, conn)
    if len(args) == 1:
        conn = args[0]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return _create_ticket_db(title, description, priority, "Open", now, now, conn)

    # New-style call: create_ticket_db(title, description, priority, status, created_at, updated_at, conn)
    if len(args) == 4:
        status, created_at, updated_at, conn = args
        return _create_ticket_db(title, description, priority, status, created_at, updated_at, conn)

    raise TypeError("create_ticket_db called with unsupported signature")


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

    if sort_by == "priority":
        query += " ORDER BY CASE UPPER(priority) WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 WHEN 'LOW' THEN 3 END"
    elif sort_by == "date":
        query += " ORDER BY created_at ASC"
    else:
        query += " ORDER BY id ASC"

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
    """Safe update that whitelists columns before building SQL to avoid dynamic injection."""
    cursor = conn.cursor()
    fields = []
    params = []

    if title is not None:
        fields.append(("title", title))
    if description is not None:
        fields.append(("description", description))
    if priority is not None:
        fields.append(("priority", priority))
    if status is not None:
        fields.append(("status", status))

    if not fields:
        return 0

    # Always update updated_at
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fields.append(("updated_at", now))

    # Validate and build SET clause with placeholders
    # perform per-column updates using fixed SQL statements to avoid dynamic SQL
    total_rows = 0
    for col, val in fields:
        if col not in VALID_UPDATE_COLUMNS:
            raise ValueError(f"Invalid column for update: {col}")
        # execute a fixed UPDATE per allowed column
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


def update_ticket_status_db(ticket_id, status, conn):
    return update_ticket_db(ticket_id, status=status, conn=conn)


def delete_ticket_db(ticket_id, conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tickets WHERE id=?", (ticket_id,))
    conn.commit()
    return cursor.rowcount


def create_ticket_logic(title, description, priority, conn):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return create_ticket_db(title, description, priority, "Open", now, now, conn)


def main(conn=None):
    if conn is None:
        conn = get_connection()
        setup_db(conn)

    choice = input()
    if choice.strip() == "1":
        title = input()
        desc = input()
        priority = input()
        create_ticket_db(title, desc, priority, "Open", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), conn)
    return
