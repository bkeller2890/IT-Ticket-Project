import sqlite3
import unittest
from unittest.mock import patch

from tests.ticket_tester import (create_ticket_db, delete_ticket_db, main,
                                 setup_db, update_ticket_status_db,
                                 view_tickets_db)


class TestTicketSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = sqlite3.connect(":memory:")  # In-memory DB
        setup_db(cls.conn)

    def setUp(self):
        # Clear tickets table before each test
        self.conn.execute("DELETE FROM tickets")
        self.conn.commit()

    def test_create_and_view_ticket(self):
        tid = create_ticket_db("Server Down", "Main server is down", "High", self.conn)
        tickets = view_tickets_db(self.conn)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0][0], tid)
        self.assertEqual(tickets[0][1], "Server Down")
        self.assertEqual(tickets[0][3], "High")

    def test_update_ticket_status(self):
        tid = create_ticket_db("Ticket1", "Open ticket", "Low", self.conn)
        rows = update_ticket_status_db(tid, "Closed", self.conn)
        self.assertEqual(rows, 1)
        ticket = view_tickets_db(self.conn, filter_status="Closed")[0]
        self.assertEqual(ticket[0], tid)

    def test_delete_ticket(self):
        tid = create_ticket_db("Delete Me", "Test delete", "Medium", self.conn)
        rows = delete_ticket_db(tid, self.conn)
        self.assertEqual(rows, 1)
        tickets = view_tickets_db(self.conn)
        self.assertEqual(len(tickets), 0)

    def test_filter_by_status(self):
        # Create two tickets; only the second will be closed for filtering
        create_ticket_db("Ticket1", "Open ticket", "Low", self.conn)
        tid2 = create_ticket_db("Ticket2", "Closed ticket", "Medium", self.conn)
        update_ticket_status_db(tid2, "Closed", self.conn)
        closed_tickets = view_tickets_db(self.conn, filter_status="Closed")
        self.assertEqual(len(closed_tickets), 1)
        self.assertEqual(closed_tickets[0][0], tid2)

    def test_sort_by_priority(self):
        create_ticket_db("Low Priority", "Desc", "Low", self.conn)
        create_ticket_db("High Priority", "Desc", "High", self.conn)
        create_ticket_db("Medium Priority", "Desc", "Medium", self.conn)
        tickets = view_tickets_db(self.conn, sort_by="priority")
        self.assertEqual(tickets[0][1], "High Priority")
        self.assertEqual(tickets[1][1], "Medium Priority")
        self.assertEqual(tickets[2][1], "Low Priority")

    def test_search_tickets(self):
        create_ticket_db("Network Issue", "Internet is slow", "Medium", self.conn)
        create_ticket_db("Server Issue", "Server down", "High", self.conn)
        results = view_tickets_db(self.conn, search_keyword="Server")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "Server Issue")

    def test_update_invalid_ticket(self):
        rows = update_ticket_status_db(
            9999, "Closed", self.conn
        )  # ID that doesn't exist
        self.assertEqual(rows, 0)  # No rows should be updated

    def test_delete_invalid_ticket(self):
        rows = delete_ticket_db(9999, self.conn)
        self.assertEqual(rows, 0)  # No rows should be deleted

    def test_search_no_results(self):
        create_ticket_db("Network Issue", "Internet is slow", "Medium", self.conn)
        results = view_tickets_db(
            self.conn, search_keyword="Server"
        )  # No matching ticket
        self.assertEqual(len(results), 0)

    def test_filter_status_no_match(self):
        create_ticket_db("Ticket1", "Open ticket", "Low", self.conn)
        closed_tickets = view_tickets_db(
            self.conn, filter_status="Closed"
        )  # No closed tickets yet
        self.assertEqual(len(closed_tickets), 0)

    def test_priority_sort_case_insensitive(self):
        create_ticket_db("low", "Desc", "low", self.conn)
        create_ticket_db("HIGH", "Desc", "HIGH", self.conn)
        create_ticket_db("Medium", "Desc", "Medium", self.conn)
        tickets = view_tickets_db(self.conn, sort_by="priority")
        self.assertEqual(tickets[0][3].capitalize(), "High")
        self.assertEqual(tickets[1][3].capitalize(), "Medium")
        self.assertEqual(tickets[2][3].capitalize(), "Low")

    def test_empty_database(self):
        tickets = view_tickets_db(self.conn)
        self.assertEqual(len(tickets), 0)


class TestInteractiveMenu(unittest.TestCase):
    @patch("builtins.input", side_effect=["1", "Test Ticket", "Desc", "High", "8"])
    @patch("builtins.print")  # optional: capture print output
    def test_create_ticket_via_menu(self, mock_print, mock_input):
        conn = sqlite3.connect(":memory:")
        setup_db(conn)

        main(conn=conn)  # run menu with simulated inputs

        # Verify ticket was created
        tickets = view_tickets_db(conn)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0][1], "Test Ticket")
        self.assertEqual(tickets[0][3], "High")


if __name__ == "__main__":
    unittest.main()
