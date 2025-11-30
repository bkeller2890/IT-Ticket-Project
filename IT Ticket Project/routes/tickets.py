# routes/tickets.py
from flask import Blueprint, flash, redirect, render_template, request, url_for
from models.ticket_model import PRIORITIES, STATUSES
from services.ticket_service import (count_tickets_service,
                                     create_ticket_service,
                                     delete_ticket_service, get_ticket_service,
                                     list_tickets_service,
                                     update_ticket_service)

bp = Blueprint("tickets", __name__)


# -------------------------
# Helper
# -------------------------
def get_ticket_form():
    """Extracts ticket data from request form"""
    return {
        "title": request.form.get("title", "").strip(),
        "description": request.form.get("description", "").strip(),
        "priority": request.form.get("priority"),
        "status": request.form.get("status"),
    }


# -------------------------
# Home / List Tickets
# -------------------------
@bp.route("/")
def home():
    page = request.args.get("page", 1, type=int)
    per_page = 10
    search = request.args.get("search", "").strip()
    filter_status = request.args.get("filter_status")
    sort_by = request.args.get("sort_by")

    tickets = list_tickets_service(
        filter_status=filter_status,
        sort_by=sort_by,
        search=search,
        page=page,
        per_page=per_page,
    )
    total = count_tickets_service(filter_status=filter_status, search=search)
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "home.html",
        tickets=tickets,
        current_page=page,
        total_pages=total_pages,
        search=search,
        filter_status=filter_status,
        sort_by=sort_by,
        STATUSES=STATUSES,
    )


# -------------------------
# Create Ticket
# -------------------------
@bp.route("/create", methods=["GET", "POST"])
def create_ticket_route():
    ticket = {"title": "", "description": "", "priority": ""}
    if request.method == "POST":
        ticket = get_ticket_form()
        success, errors = create_ticket_service(
            ticket["title"], ticket["description"], ticket["priority"]
        )
        if not success:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "create_ticket.html",
                ticket=ticket,
                PRIORITIES=PRIORITIES,
                STATUSES=STATUSES,
            )

        flash("Ticket created!", "success")
        return redirect(url_for("tickets.home"))

    return render_template(
        "create_ticket.html", ticket=ticket, PRIORITIES=PRIORITIES, STATUSES=STATUSES
    )


# -------------------------
# Update Ticket
# -------------------------
@bp.route("/update/<int:ticket_id>", methods=["GET", "POST"])
def update_ticket_route(ticket_id):
    ticket = get_ticket_service(ticket_id)
    if not ticket:
        flash("Ticket not found.", "danger")
        return redirect(url_for("tickets.home"))

    if request.method == "POST":
        form_data = get_ticket_form()
        success, errors = update_ticket_service(
            ticket_id,
            form_data["title"],
            form_data["description"],
            form_data["priority"],
            form_data["status"],
        )
        if not success:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "update_ticket.html",
                ticket=form_data,
                PRIORITIES=PRIORITIES,
                STATUSES=STATUSES,
            )

        flash("Ticket updated!", "success")
        return redirect(url_for("tickets.home"))

    return render_template(
        "update_ticket.html", ticket=ticket, PRIORITIES=PRIORITIES, STATUSES=STATUSES
    )


# -------------------------
# Delete Ticket
# -------------------------
@bp.route("/delete/<int:ticket_id>", methods=["POST"])
def delete_ticket_route(ticket_id):
    success, _ = delete_ticket_service(ticket_id)
    if success:
        flash("Ticket deleted!", "success")
    else:
        flash("Ticket not found!", "danger")
    return redirect(url_for("tickets.home"))
