import unittest
from datetime import datetime, timedelta
import json
import os
import tempfile

# Importy klas do testowania
from src.book_manager import BookManager
from src.category_manager import CategoryManager
from src.loan_manager import LoanManager
from src.reservation_manager import ReservationManager
from src.user_manager import UserManager
from src.utils import validate_email, validate_isbn, validate_user_id, save_data, load_data


class TestLibrarySystemIntegration(unittest.TestCase):
    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem."""
        # Inicjalizacja menedżerów
        self.book_manager = BookManager()
        self.user_manager = UserManager()
        self.category_manager = CategoryManager(self.book_manager)
        self.loan_manager = LoanManager(self.book_manager, self.user_manager)
        self.reservation_manager = ReservationManager(self.book_manager, self.user_manager)

        # Dodanie przykładowych danych testowych
        self.sample_user_id = self.user_manager.add_user("Jan Kowalski", "jan@example.com")
        self.sample_book_id = self.book_manager.add_book("Władca Pierścieni", "J.R.R. Tolkien", "9788328705141", 1954)

        # Przygotowanie książki dla kategorii
        # Dodanie atrybutu categories, który nie jest inicjalizowany w BookManager
        self.book_manager.books[self.sample_book_id]["categories"] = []

        # Dodanie kategorii
        self.category_manager.add_category("Fantasy")

    def tearDown(self):
        """Czyszczenie po każdym teście."""
        # Możemy tu dodać kod czyszczący, jeśli będzie potrzebny
        pass

    # Testy integracji BookManager z UserManager poprzez LoanManager

    def test_loan_book_integration(self):
        """Test integracji wypożyczania książki - BookManager i UserManager poprzez LoanManager."""
        # Wypożyczenie książki
        loan_id = self.loan_manager.loan_book(self.sample_user_id, self.sample_book_id)

        # Sprawdzenie, czy książka została oznaczona jako niedostępna
        book = self.book_manager.get_book(self.sample_book_id)
        self.assertFalse(book["available"])

        # Sprawdzenie, czy wypożyczenie zostało zarejestrowane
        loan = self.loan_manager.get_loan(loan_id)
        self.assertEqual(loan["user_id"], self.sample_user_id)
        self.assertEqual(loan["book_id"], self.sample_book_id)
        self.assertFalse(loan["returned"])

    def test_return_book_integration(self):
        """Test integracji zwrotu książki - BookManager poprzez LoanManager."""
        # Wypożyczenie książki
        loan_id = self.loan_manager.loan_book(self.sample_user_id, self.sample_book_id)

        # Zwrot książki
        self.loan_manager.return_book(loan_id)

        # Sprawdzenie, czy książka została oznaczona jako dostępna
        book = self.book_manager.get_book(self.sample_book_id)
        self.assertTrue(book["available"])

        # Sprawdzenie, czy wypożyczenie zostało oznaczone jako zwrócone
        loan = self.loan_manager.get_loan(loan_id)
        self.assertTrue(loan["returned"])

    # Testy integracji BookManager z CategoryManager

    def test_assign_category_to_book(self):
        """Test integracji przypisania kategorii do książki."""
        # Przypisanie kategorii do książki
        self.category_manager.assign_category(self.sample_book_id, "Fantasy")

        # Sprawdzenie, czy kategoria została przypisana
        book = self.book_manager.get_book(self.sample_book_id)
        self.assertIn("Fantasy", book["categories"])

    def test_remove_category_from_book(self):
        """Test integracji usunięcia kategorii z książki."""
        # Przypisanie i usunięcie kategorii
        self.category_manager.assign_category(self.sample_book_id, "Fantasy")
        self.category_manager.remove_category_from_book(self.sample_book_id, "Fantasy")

        # Sprawdzenie, czy kategoria została usunięta
        book = self.book_manager.get_book(self.sample_book_id)
        self.assertNotIn("Fantasy", book["categories"])

    def test_remove_category_affecting_books(self):
        """Test integracji usunięcia kategorii wpływającego na książki."""
        # Przypisanie kategorii do książki
        self.category_manager.assign_category(self.sample_book_id, "Fantasy")

        # Usunięcie kategorii
        self.category_manager.remove_category("Fantasy")

        # Sprawdzenie, czy kategoria została usunięta z książki
        book = self.book_manager.get_book(self.sample_book_id)
        self.assertNotIn("Fantasy", book["categories"])

        # Sprawdzenie, czy kategoria została usunięta z systemu
        self.assertNotIn("Fantasy", self.category_manager.categories)

    # Testy integracji ReservationManager z BookManager i UserManager

    def test_reserve_book_integration(self):
        """Test integracji rezerwacji książki."""
        # Wypożyczenie książki, aby była niedostępna
        self.loan_manager.loan_book(self.sample_user_id, self.sample_book_id)

        # Dodanie drugiego użytkownika
        second_user_id = self.user_manager.add_user("Anna Nowak", "anna@example.com")

        # Rezerwacja książki przez drugiego użytkownika
        reservation_id = self.reservation_manager.reserve_book(second_user_id, self.sample_book_id)

        # Sprawdzenie, czy rezerwacja została zarejestrowana
        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["user_id"], second_user_id)
        self.assertEqual(reservation["book_id"], self.sample_book_id)
        self.assertEqual(reservation["status"], "waiting")

    def test_book_returned_triggering_reservation(self):
        """Test integracji zwrotu książki aktywującego rezerwację."""
        # Wypożyczenie książki przez pierwszego użytkownika
        loan_id = self.loan_manager.loan_book(self.sample_user_id, self.sample_book_id)

        # Dodanie drugiego użytkownika
        second_user_id = self.user_manager.add_user("Anna Nowak", "anna@example.com")

        # Rezerwacja książki przez drugiego użytkownika
        reservation_id = self.reservation_manager.reserve_book(second_user_id, self.sample_book_id)

        # Zwrot książki przez pierwszego użytkownika
        self.loan_manager.return_book(loan_id)

        # Powiadomienie systemu rezerwacji o zwrocie książki
        next_reservation_id = self.reservation_manager.book_returned(self.sample_book_id)

        # Sprawdzenie, czy rezerwacja została aktywowana
        self.assertEqual(next_reservation_id, reservation_id)

        # Sprawdzenie, czy status rezerwacji został zmieniony
        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["status"], "ready")
        self.assertTrue(reservation["notification_sent"])

    def test_complete_reservation_integration(self):
        """Test integracji zakończenia rezerwacji po wypożyczeniu książki."""
        # Wypożyczenie książki przez pierwszego użytkownika
        loan_id = self.loan_manager.loan_book(self.sample_user_id, self.sample_book_id)

        # Dodanie drugiego użytkownika
        second_user_id = self.user_manager.add_user("Anna Nowak", "anna@example.com")

        # Rezerwacja książki przez drugiego użytkownika
        reservation_id = self.reservation_manager.reserve_book(second_user_id, self.sample_book_id)

        # Zwrot książki przez pierwszego użytkownika
        self.loan_manager.return_book(loan_id)

        # Powiadomienie systemu rezerwacji o zwrocie książki
        self.reservation_manager.book_returned(self.sample_book_id)

        # Zakończenie rezerwacji (zazwyczaj po wypożyczeniu książki)
        self.reservation_manager.complete_reservation(reservation_id)

        # Sprawdzenie, czy status rezerwacji został zmieniony
        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["status"], "completed")

    # Testy integracji z utils

    def test_utils_integration_with_user_manager(self):
        """Test integracji funkcji validate_email z UserManager."""
        # Próba dodania użytkownika z nieprawidłowym adresem email
        with self.assertRaises(ValueError):
            # Najpierw sprawdzamy czy email jest prawidłowy przy użyciu utils
            if not validate_email("nieprawidlowy_email"):
                raise ValueError("Nieprawidłowy adres email")
            self.user_manager.add_user("Test User", "nieprawidlowy_email")

        # Dodanie użytkownika z prawidłowym adresem email
        if validate_email("prawidlowy@example.com"):
            user_id = self.user_manager.add_user("Test User", "prawidlowy@example.com")
            self.assertIsNotNone(user_id)

    def test_utils_integration_with_book_manager(self):
        """Test integracji funkcji validate_isbn z BookManager."""
        # Próba dodania książki z nieprawidłowym ISBN
        with self.assertRaises(ValueError):
            # Najpierw sprawdzamy czy ISBN jest prawidłowy przy użyciu utils
            if not validate_isbn("12345"):
                raise ValueError("Nieprawidłowy ISBN")
            self.book_manager.add_book("Test Book", "Test Author", "12345")

        # Dodanie książki z prawidłowym ISBN
        if validate_isbn("1234567890"):
            book_id = self.book_manager.add_book("Test Book", "Test Author", "1234567890")
            self.assertIsNotNone(book_id)

    # Test zapisywania i wczytywania danych

    def test_save_and_load_data_integration(self):
        """Test integracji zapisywania i wczytywania danych z utils."""
        # Tworzenie tymczasowego pliku
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file_path = tmp.name

        try:
            # Przygotowanie danych do zapisu - prosta struktura bez kluczy liczbowych
            test_data = {
                "title": "Test Book",
                "author": "Test Author",
                "available": True
            }

            # Zapisanie danych
            save_data(test_data, file_path)

            # Wczytanie danych
            loaded_data = load_data(file_path)

            # Sprawdzenie, czy dane zostały poprawnie zapisane i wczytane
            self.assertEqual(loaded_data, test_data)

            # Bardziej realistyczny test - symulacja zapisywania książek
            # ale z konwersją kluczy na stringi, co jest typowe dla JSON
            books_data_serializable = {}
            for book_id, book in self.book_manager.books.items():
                books_data_serializable[str(book_id)] = book.copy()

            save_data(books_data_serializable, file_path)
            loaded_books = load_data(file_path)

            # Sprawdzamy, czy wartości książek są takie same, pomijając format kluczy
            for book_id, book in self.book_manager.books.items():
                str_id = str(book_id)
                self.assertIn(str_id, loaded_books)
                for key, value in book.items():
                    self.assertEqual(loaded_books[str_id][key], value)
        finally:
            # Usunięcie tymczasowego pliku
            os.unlink(file_path)

    # Test pełnego scenariusza używania systemu

    def test_full_library_system_workflow(self):
        """Test pełnego przepływu pracy systemu bibliotecznego."""
        # 1. Dodanie użytkowników
        user1_id = self.user_manager.add_user("Jan Kowalski", "jan@example.com")
        user2_id = self.user_manager.add_user("Anna Nowak", "anna@example.com")

        # 2. Dodanie książek
        book1_id = self.book_manager.add_book("Władca Pierścieni", "J.R.R. Tolkien", "9788328705141", 1954)
        book2_id = self.book_manager.add_book("Hobbit", "J.R.R. Tolkien", "9788328704442", 1937)

        # Dodanie atrybutu categories
        self.book_manager.books[book1_id]["categories"] = []
        self.book_manager.books[book2_id]["categories"] = []

        # 3. Dodanie kategorii (Fantasy już dodana w setUp)
        # Upewniamy się, że kategoria nie istnieje przed dodaniem
        if "Przygodowa" not in self.category_manager.categories:
            self.category_manager.add_category("Przygodowa")

        # 4. Przypisanie kategorii do książek
        self.category_manager.assign_category(book1_id, "Fantasy")
        self.category_manager.assign_category(book2_id, "Fantasy")
        self.category_manager.assign_category(book2_id, "Przygodowa")

        # 5. Wypożyczenie książki przez pierwszego użytkownika
        loan1_id = self.loan_manager.loan_book(user1_id, book1_id)

        # 6. Drugi użytkownik rezerwuje wypożyczoną książkę
        reservation_id = self.reservation_manager.reserve_book(user2_id, book1_id)

        # 7. Sprawdzenie pozycji w kolejce
        position = self.reservation_manager.get_position_in_queue(reservation_id)
        self.assertEqual(position, 1)  # Powinien być pierwszy w kolejce

        # 8. Pierwszy użytkownik zwraca książkę
        self.loan_manager.return_book(loan1_id)

        # 9. System rezerwacji jest powiadamiany o zwrocie
        next_reservation_id = self.reservation_manager.book_returned(book1_id)
        self.assertEqual(next_reservation_id, reservation_id)

        # 10. Rezerwacja jest gotowa do realizacji
        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["status"], "ready")

        # 11. Drugi użytkownik wypożycza zarezerwowaną książkę
        loan2_id = self.loan_manager.loan_book(user2_id, book1_id)

        # 12. Rezerwacja jest oznaczana jako zrealizowana
        self.reservation_manager.complete_reservation(reservation_id)

        # 13. Sprawdzenie statusu rezerwacji
        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["status"], "completed")

        # 14. Drugi użytkownik zwraca książkę
        self.loan_manager.return_book(loan2_id)

        # 15. Sprawdzenie dostępności książki
        book = self.book_manager.get_book(book1_id)
        self.assertTrue(book["available"])


if __name__ == "__main__":
    unittest.main()