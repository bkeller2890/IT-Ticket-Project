"""Model constants re-exported from the single DB module.

Keep constants here for backward compatibility: import from
`models.ticket_model` is still supported but the source of truth
is `database.py`.
"""

from database import PRIORITIES, STATUSES

__all__ = ["PRIORITIES", "STATUSES"]
