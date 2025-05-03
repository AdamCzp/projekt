import unittest
import os
import tempfile

from src.book_manager import BookManager
from src.category_manager import CategoryManager
from src.loan_manager import LoanManager
from src.reservation_manager import ReservationManager
from src.user_manager import UserManager
from src.utils import validate_email, validate_isbn, validate_user_id, save_data, load_data


class TestLibrarySystemIntegration(unittest.TestCase):
    def setUp(self):
        self.book_manager = BookManager()
        self.user_manager = UserManager()
        self.category_manager = CategoryManager(self.book_manager)
        self.loan_manager = LoanManager(self.book_manager, self.user_manager)
        self.reservation_manager = ReservationManager(self.book_manager, self.user_manager)

        self.sample_user_id = self.user_manager.add_user("Jan Kowalski", "jan@example.com")
        self.sample_book_id = self.book_manager.add_book("Władca Pierścieni", "J.R.R. Tolkien", "9788328705141", 1954)

        self.book_manager.books[self.sample_book_id]["categories"] = []

        self.category_manager.add_category("Fantasy")

    def tearDown(self):
        pass


    def test_loan_book_integration(self):
        loan_id = self.loan_manager.loan_book(self.sample_user_id, self.sample_book_id)

        book = self.book_manager.get_book(self.sample_book_id)
        self.assertFalse(book["available"])

        loan = self.loan_manager.get_loan(loan_id)
        self.assertEqual(loan["user_id"], self.sample_user_id)
        self.assertEqual(loan["book_id"], self.sample_book_id)
        self.assertFalse(loan["returned"])

    def test_return_book_integration(self):
        loan_id = self.loan_manager.loan_book(self.sample_user_id, self.sample_book_id)

        self.loan_manager.return_book(loan_id)

        book = self.book_manager.get_book(self.sample_book_id)
        self.assertTrue(book["available"])

        loan = self.loan_manager.get_loan(loan_id)
        self.assertTrue(loan["returned"])


    def test_assign_category_to_book(self):

        self.category_manager.assign_category(self.sample_book_id, "Fantasy")

        book = self.book_manager.get_book(self.sample_book_id)
        self.assertIn("Fantasy", book["categories"])

    def test_remove_category_from_book(self):

        self.category_manager.assign_category(self.sample_book_id, "Fantasy")
        self.category_manager.remove_category_from_book(self.sample_book_id, "Fantasy")

        book = self.book_manager.get_book(self.sample_book_id)
        self.assertNotIn("Fantasy", book["categories"])

    def test_remove_category_affecting_books(self):

        self.category_manager.assign_category(self.sample_book_id, "Fantasy")

        self.category_manager.remove_category("Fantasy")

        book = self.book_manager.get_book(self.sample_book_id)
        self.assertNotIn("Fantasy", book["categories"])

        self.assertNotIn("Fantasy", self.category_manager.categories)


    def test_reserve_book_integration(self):
        self.loan_manager.loan_book(self.sample_user_id, self.sample_book_id)

        second_user_id = self.user_manager.add_user("Anna Nowak", "anna@example.com")

        reservation_id = self.reservation_manager.reserve_book(second_user_id, self.sample_book_id)

        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["user_id"], second_user_id)
        self.assertEqual(reservation["book_id"], self.sample_book_id)
        self.assertEqual(reservation["status"], "waiting")

    def test_book_returned_triggering_reservation(self):

        loan_id = self.loan_manager.loan_book(self.sample_user_id, self.sample_book_id)

        second_user_id = self.user_manager.add_user("Anna Nowak", "anna@example.com")

        reservation_id = self.reservation_manager.reserve_book(second_user_id, self.sample_book_id)

        self.loan_manager.return_book(loan_id)

        next_reservation_id = self.reservation_manager.book_returned(self.sample_book_id)

        self.assertEqual(next_reservation_id, reservation_id)

        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["status"], "ready")
        self.assertTrue(reservation["notification_sent"])

    def test_complete_reservation_integration(self):
        loan_id = self.loan_manager.loan_book(self.sample_user_id, self.sample_book_id)

        second_user_id = self.user_manager.add_user("Anna Nowak", "anna@example.com")

        reservation_id = self.reservation_manager.reserve_book(second_user_id, self.sample_book_id)

        self.loan_manager.return_book(loan_id)

        self.reservation_manager.book_returned(self.sample_book_id)

        self.reservation_manager.complete_reservation(reservation_id)

        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["status"], "completed")


    def test_utils_integration_with_user_manager(self):
        with self.assertRaises(ValueError):
            if not validate_email("nieprawidlowy_email"):
                raise ValueError("Nieprawidłowy adres email")
            self.user_manager.add_user("Test User", "nieprawidlowy_email")

        if validate_email("prawidlowy@example.com"):
            user_id = self.user_manager.add_user("Test User", "prawidlowy@example.com")
            self.assertIsNotNone(user_id)

    def test_utils_integration_with_book_manager(self):
        with self.assertRaises(ValueError):
            if not validate_isbn("12345"):
                raise ValueError("Nieprawidłowy ISBN")
            self.book_manager.add_book("Test Book", "Test Author", "12345")

        if validate_isbn("1234567890"):
            book_id = self.book_manager.add_book("Test Book", "Test Author", "1234567890")
            self.assertIsNotNone(book_id)


    def test_save_and_load_data_integration(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file_path = tmp.name

        try:
            test_data = {
                "title": "Test Book",
                "author": "Test Author",
                "available": True
            }

            save_data(test_data, file_path)

            loaded_data = load_data(file_path)

            self.assertEqual(loaded_data, test_data)

            books_data_serializable = {}
            for book_id, book in self.book_manager.books.items():
                books_data_serializable[str(book_id)] = book.copy()

            save_data(books_data_serializable, file_path)
            loaded_books = load_data(file_path)

            for book_id, book in self.book_manager.books.items():
                str_id = str(book_id)
                self.assertIn(str_id, loaded_books)
                for key, value in book.items():
                    self.assertEqual(loaded_books[str_id][key], value)
        finally:
            os.unlink(file_path)


    def test_full_library_system_workflow(self):
        user1_id = self.user_manager.add_user("Jan Kowalski", "jan@example.com")
        user2_id = self.user_manager.add_user("Anna Nowak", "anna@example.com")

        book1_id = self.book_manager.add_book("Władca Pierścieni", "J.R.R. Tolkien", "9788328705141", 1954)
        book2_id = self.book_manager.add_book("Hobbit", "J.R.R. Tolkien", "9788328704442", 1937)

        self.book_manager.books[book1_id]["categories"] = []
        self.book_manager.books[book2_id]["categories"] = []

        if "Przygodowa" not in self.category_manager.categories:
            self.category_manager.add_category("Przygodowa")

        self.category_manager.assign_category(book1_id, "Fantasy")
        self.category_manager.assign_category(book2_id, "Fantasy")
        self.category_manager.assign_category(book2_id, "Przygodowa")

        loan1_id = self.loan_manager.loan_book(user1_id, book1_id)

        reservation_id = self.reservation_manager.reserve_book(user2_id, book1_id)

        position = self.reservation_manager.get_position_in_queue(reservation_id)
        self.assertEqual(position, 1)  # Powinien być pierwszy w kolejce

        self.loan_manager.return_book(loan1_id)

        next_reservation_id = self.reservation_manager.book_returned(book1_id)
        self.assertEqual(next_reservation_id, reservation_id)

        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["status"], "ready")

        loan2_id = self.loan_manager.loan_book(user2_id, book1_id)

        self.reservation_manager.complete_reservation(reservation_id)

        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["status"], "completed")

        self.loan_manager.return_book(loan2_id)

        book = self.book_manager.get_book(book1_id)
        self.assertTrue(book["available"])


if __name__ == "__main__":
    unittest.main()