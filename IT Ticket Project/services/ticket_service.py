# services/ticket_service.py
from typing import Any, List, Optional, Tuple

from database import db_session
from models.ticket import (count_tickets, create_ticket, delete_ticket,
                           get_ticket, list_tickets, update_ticket)
from models.ticket_model import PRIORITIES, STATUSES
from validators import validate_ticket

# -------------------------
# Ticket Service Helpers
# -------------------------


def handle_db_operation(func, *args, **kwargs) -> Tuple[bool, Optional[List[str]]]:
    """
    Executes a database operation safely within a session.
    Returns (success: bool, errors: list or None)
    """
    try:
        with db_session() as conn:
            result = func(conn, *args, **kwargs)
        return True, result if result is not None else None
    except Exception as e:
        return False, [str(e)]


# -------------------------
# Create Ticket
# -------------------------
def create_ticket_service(
    title: str, description: str, priority: str
) -> Tuple[bool, Optional[List[str]]]:
    """
    Validates and creates a new ticket.
    Returns (success: bool, errors: list or None)
    """
    errors = validate_ticket(title, description, priority, PRIORITIES=PRIORITIES)
    if errors:
        return False, errors

    return handle_db_operation(create_ticket, title, description, priority)


# -------------------------
# Update Ticket
# -------------------------
def update_ticket_service(
    ticket_id: int, title: str, description: str, priority: str, status: str
) -> Tuple[bool, Optional[List[str]]]:
    """
    Validates and updates an existing ticket.
    Returns (success: bool, errors: list or None)
    """
    errors = validate_ticket(
        title, description, priority, status, PRIORITIES=PRIORITIES, STATUSES=STATUSES
    )
    if errors:
        return False, errors

    return handle_db_operation(
        update_ticket, ticket_id, title, description, priority, status
    )


# -------------------------
# Delete Ticket
# -------------------------
def delete_ticket_service(ticket_id: int) -> Tuple[bool, Optional[List[str]]]:
    """
    Deletes a ticket by ID.
    Returns (success: bool, errors: list or None)
    """
    return handle_db_operation(delete_ticket, ticket_id)


# -------------------------
# Get Single Ticket
# -------------------------
def get_ticket_service(ticket_id: int) -> Any:
    """
    Retrieves a single ticket by ID.
    Returns ticket row or None.
    """
    with db_session() as conn:
        return get_ticket(conn, ticket_id)


# -------------------------
# List Tickets
# -------------------------
def list_tickets_service(
    filter_status: Optional[str] = None,
    sort_by: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    per_page: int = 10,
):
    """
    Retrieves a paginated list of tickets with optional filters and sorting.
    """
    offset = (page - 1) * per_page
    with db_session() as conn:
        return list_tickets(
            conn,
            filter_status=filter_status,
            sort_by=sort_by,
            search=search,
            offset=offset,
            limit=per_page,
        )


# -------------------------
# Count Tickets
# -------------------------
def count_tickets_service(
    filter_status: Optional[str] = None, search: Optional[str] = None
) -> int:
    """
    Returns total number of tickets matching optional filters.
    """
    with db_session() as conn:
        return count_tickets(conn, filter_status=filter_status, search=search)
