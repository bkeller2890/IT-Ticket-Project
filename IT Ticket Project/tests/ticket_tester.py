"""Backward-compatible test shim that re-exports the helpers implemented in tests.helpers.

Tests import functions from this module historically; to avoid duplicating code we
implement the shared helpers in `tests/helpers.py` and re-export them here.
"""

from tests.helpers import (create_ticket_db, create_ticket_logic,
                           delete_ticket_db, get_connection, get_ticket_count,
                           main, setup_db, update_ticket_db,
                           update_ticket_status_db, view_tickets_db)

__all__ = [
    "get_connection",
    "setup_db",
    "create_ticket_db",
    "view_tickets_db",
    "get_ticket_count",
    "update_ticket_db",
    "update_ticket_status_db",
    "delete_ticket_db",
    "create_ticket_logic",
    "main",
]
