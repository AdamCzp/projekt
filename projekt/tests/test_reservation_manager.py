import unittest
from datetime import datetime, timedelta
from src.reservation_manager import ReservationManager  # zakładamy, że klasa jest w pliku reservation_manager.py

class DummyBookManager:
    def __init__(self):
        self.books = {}

    def add_book(self, book_id, available=False):
        self.books[book_id] = {"id": book_id, "available": available}

    def get_book(self, book_id):
        if book_id not in self.books:
            raise ValueError("Book not found")
        return self.books[book_id]

class DummyUserManager:
    def __init__(self):
        self.users = {}

    def add_user(self, user_id):
        self.users[user_id] = {"id": user_id}

    def get_user(self, user_id):
        if user_id not in self.users:
            raise ValueError("User not found")
        return self.users[user_id]

class TestReservationManager(unittest.TestCase):
    def setUp(self):
        self.book_manager = DummyBookManager()
        self.user_manager = DummyUserManager()
        self.rm = ReservationManager(self.book_manager, self.user_manager)

        self.user_manager.add_user(1)
        self.book_manager.add_book(101, available=False)

    def test_successful_reservation(self):
        reservation_id = self.rm.reserve_book(1, 101)
        reservation = self.rm.get_reservation(reservation_id)
        self.assertEqual(reservation["user_id"], 1)
        self.assertEqual(reservation["book_id"], 101)
        self.assertEqual(reservation["status"], "waiting")

    def test_duplicate_reservation(self):
        self.rm.reserve_book(1, 101)
        with self.assertRaises(ValueError):
            self.rm.reserve_book(1, 101)

    def test_cancel_reservation(self):
        reservation_id = self.rm.reserve_book(1, 101)
        result = self.rm.cancel_reservation(reservation_id)
        self.assertTrue(result)
        reservation = self.rm.get_reservation(reservation_id)
        self.assertEqual(reservation["status"], "cancelled")

    def test_complete_reservation(self):
        reservation_id = self.rm.reserve_book(1, 101)
        self.rm.book_returned(101)  # ustawia status na "ready"
        result = self.rm.complete_reservation(reservation_id)
        self.assertTrue(result)
        reservation = self.rm.get_reservation(reservation_id)
        self.assertEqual(reservation["status"], "completed")

    def test_expired_reservation(self):
        reservation_id = self.rm.reserve_book(1, 101)
        self.rm.book_returned(101)
        self.rm.reservations[reservation_id]["expiry_date"] = (datetime.now() - timedelta(days=1)).isoformat()
        expired = self.rm.check_expired_reservations()
        self.assertIn(reservation_id, expired)
        self.assertEqual(self.rm.reservations[reservation_id]["status"], "expired")

    def test_position_in_queue(self):
        self.user_manager.add_user(2)
        self.book_manager.add_book(102, available=False)
        res1 = self.rm.reserve_book(1, 102)
        res2 = self.rm.reserve_book(2, 102)
        self.assertEqual(self.rm.get_position_in_queue(res1), 1)
        self.assertEqual(self.rm.get_position_in_queue(res2), 2)

    def test_reserve_unavailable_book(self):
        self.book_manager.books[101]["available"] = True
        with self.assertRaises(ValueError):
            self.rm.reserve_book(1, 101)

if __name__ == "__main__":
    unittest.main()
