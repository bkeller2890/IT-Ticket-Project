# models/ticket.py

# -------------------------
# CRUD Operations
# -------------------------

def create_ticket(conn, title: str, description: str, priority: str) -> int:
    """Insert a new ticket with default status 'Open'. Returns the newly created ticket ID."""
    with conn:
        cur = conn.execute("""
            INSERT INTO tickets (title, description, priority, status)
            VALUES (?, ?, ?, 'Open')
        """, (title, description, priority))
        return cur.lastrowid


def update_ticket(conn, ticket_id: int, title: str, description: str, priority: str, status: str) -> int:
    """Update an existing ticket. Returns the number of rows affected."""
    with conn:
        cur = conn.execute("""
            UPDATE tickets 
            SET title=?, description=?, priority=?, status=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (title, description, priority, status, ticket_id))
        return cur.rowcount


def delete_ticket(conn, ticket_id: int) -> int:
    """Delete a ticket by ID. Returns number of rows affected."""
    with conn:
        cur = conn.execute("DELETE FROM tickets WHERE id=?", (ticket_id,))
        return cur.rowcount


def get_ticket(conn, ticket_id: int):
    """Retrieve a single ticket by ID. Returns None if not found."""
    cur = conn.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,))
    row = cur.fetchone()
    if not row:
        return None
    # Convert sqlite3.Row to a simple object with attribute access
    from types import SimpleNamespace
    return SimpleNamespace(**dict(row))


def list_tickets(conn, filter_status=None, sort_by=None, search=None, offset=0, limit=10):
    """
    Retrieve a list of tickets with optional filtering, search, sorting, and pagination.
    """
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []

    if filter_status:
        query += " AND status=?"
        params.append(filter_status)

    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term])

    if sort_by in ("priority", "status", "created_at"):
        query += f" ORDER BY {sort_by}"

    query += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cur = conn.execute(query, params)
    rows = cur.fetchall()
    from types import SimpleNamespace
    return [SimpleNamespace(**dict(r)) for r in rows]


def count_tickets(conn, filter_status=None, search=None) -> int:
    """
    Return the total number of tickets, optionally filtered and searched.
    """
    query = "SELECT COUNT(*) FROM tickets WHERE 1=1"
    params = []

    if filter_status:
        query += " AND status=?"
        params.append(filter_status)

    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term])

    cur = conn.execute(query, params)
    return cur.fetchone()[0]
