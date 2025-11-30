import sqlite3

import pytest
from tests.helpers import (create_ticket_db, delete_ticket_db, main, setup_db,
                           update_ticket_status_db, view_tickets_db)


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    setup_db(c)
    yield c
    c.close()


def test_create_and_view_ticket(conn):
    tid = create_ticket_db("Server Down", "Main server is down", "High", conn)
    tickets = view_tickets_db(conn)
    assert len(tickets) == 1
    assert tickets[0][0] == tid
    assert tickets[0][1] == "Server Down"
    assert tickets[0][3] == "High"


def test_update_ticket_status(conn):
    tid = create_ticket_db("Ticket1", "Open ticket", "Low", conn)
    rows = update_ticket_status_db(tid, "Closed", conn)
    assert rows == 1
    ticket = view_tickets_db(conn, filter_status="Closed")[0]
    assert ticket[0] == tid


def test_delete_ticket(conn):
    tid = create_ticket_db("Delete Me", "Test delete", "Medium", conn)
    rows = delete_ticket_db(tid, conn)
    assert rows == 1
    tickets = view_tickets_db(conn)
    assert len(tickets) == 0


def test_filter_by_status(conn):
    create_ticket_db("Ticket1", "Open ticket", "Low", conn)
    tid2 = create_ticket_db("Ticket2", "Closed ticket", "Medium", conn)
    update_ticket_status_db(tid2, "Closed", conn)
    closed_tickets = view_tickets_db(conn, filter_status="Closed")
    assert len(closed_tickets) == 1
    assert closed_tickets[0][0] == tid2


def test_sort_by_priority(conn):
    create_ticket_db("Low Priority", "Desc", "Low", conn)
    create_ticket_db("High Priority", "Desc", "High", conn)
    create_ticket_db("Medium Priority", "Desc", "Medium", conn)
    tickets = view_tickets_db(conn, sort_by="priority")
    assert tickets[0][1] == "High Priority"
    assert tickets[1][1] == "Medium Priority"
    assert tickets[2][1] == "Low Priority"


def test_search_tickets(conn):
    create_ticket_db("Network Issue", "Internet is slow", "Medium", conn)
    create_ticket_db("Server Issue", "Server down", "High", conn)
    results = view_tickets_db(conn, search_keyword="Server")
    assert len(results) == 1
    assert results[0][1] == "Server Issue"


def test_update_invalid_ticket(conn):
    rows = update_ticket_status_db(9999, "Closed", conn)
    assert rows == 0


def test_delete_invalid_ticket(conn):
    rows = delete_ticket_db(9999, conn)
    assert rows == 0


def test_search_no_results(conn):
    create_ticket_db("Network Issue", "Internet is slow", "Medium", conn)
    results = view_tickets_db(conn, search_keyword="Server")
    assert len(results) == 0


def test_filter_status_no_match(conn):
    create_ticket_db("Ticket1", "Open ticket", "Low", conn)
    closed_tickets = view_tickets_db(conn, filter_status="Closed")
    assert len(closed_tickets) == 0


def test_priority_sort_case_insensitive(conn):
    create_ticket_db("low", "Desc", "low", conn)
    create_ticket_db("HIGH", "Desc", "HIGH", conn)
    create_ticket_db("Medium", "Desc", "Medium", conn)
    tickets = view_tickets_db(conn, sort_by="priority")
    assert tickets[0][3].capitalize() == "High"
    assert tickets[1][3].capitalize() == "Medium"
    assert tickets[2][3].capitalize() == "Low"


def test_empty_database(conn):
    tickets = view_tickets_db(conn)
    assert len(tickets) == 0


def test_create_ticket_via_menu(monkeypatch, conn):
    inputs = iter(["1", "Test Ticket", "Desc", "High", "8"])
    monkeypatch.setattr("builtins.input", lambda: next(inputs))
    main(conn=conn)
    tickets = view_tickets_db(conn)
    assert len(tickets) == 1
    assert tickets[0][1] == "Test Ticket"
    assert tickets[0][3] == "High"
