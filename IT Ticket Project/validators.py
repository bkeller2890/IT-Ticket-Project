def validate_ticket(title, description, priority, status=None, PRIORITIES=None, STATUSES=None):
    errors = []

    if not title or len(title) > 100:
        errors.append("Title must be between 1 and 100 characters.")

    if not description or len(description) < 10:
        errors.append("Description must be at least 10 characters.")

    if PRIORITIES and priority not in PRIORITIES:
        errors.append("Invalid priority selected.")

    if status and STATUSES and status not in STATUSES:
        errors.append("Invalid status selected.")

    return errors
