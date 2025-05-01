import unittest
from datetime import datetime, timedelta
import sys
import os

from src import utils
# Dodaj ścieżkę do katalogu, w którym znajdują się moduły (jeśli potrzebne)
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importy testowanych klas
from src.book_manager import BookManager
from src.category_manager import CategoryManager
from src.loan_manager import LoanManager
from src.reservation_manager import ReservationManager
from src.user_manager import UserManager
import src.utils


class TestIntegration(unittest.TestCase):
    """Testy integracyjne dla systemu bibliotecznego."""

    def setUp(self):
        """Przygotowanie środowiska przed każdym testem."""
        self.book_manager = BookManager()
        self.user_manager = UserManager()
        self.category_manager = CategoryManager(self.book_manager)
        self.loan_manager = LoanManager(self.book_manager, self.user_manager)
        self.reservation_manager = ReservationManager(self.book_manager, self.user_manager)

        # Dodaj kilka kategorii
        self.category_manager.add_category("Fantastyka")
        self.category_manager.add_category("Kryminał")
        self.category_manager.add_category("Biografia")

        # Dodaj kilku użytkowników testowych
        self.user1_id = self.user_manager.add_user("Jan Kowalski", "jan.kowalski@example.com")
        self.user2_id = self.user_manager.add_user("Anna Nowak", "anna.nowak@example.com")

        # Dodaj kilka książek testowych
        self.book1_id = self.book_manager.add_book("Władca Pierścieni", "J.R.R. Tolkien", "9788375780635", 1954)
        self.book2_id = self.book_manager.add_book("Morderstwo w Orient Expressie", "Agatha Christie", "9788327154644",
                                                   1934)
        self.book3_id = self.book_manager.add_book("Steve Jobs", "Walter Isaacson", "9788324633562", 2011)

        # Inicjalizuj pole categories dla każdej książki (potrzebne dla CategoryManager)
        for book_id in [self.book1_id, self.book2_id, self.book3_id]:
            self.book_manager.books[book_id]["categories"] = []

        # Przypisz kategorie do książek
        self.category_manager.assign_category(self.book1_id, "Fantastyka")
        self.category_manager.assign_category(self.book2_id, "Kryminał")
        self.category_manager.assign_category(self.book3_id, "Biografia")

    def test_wypozyczenie_i_zwrot_ksiazki(self):
        """Test integracyjny wypożyczenia i zwrotu książki."""
        # 1. Użytkownik wypożycza książkę
        loan_id = self.loan_manager.loan_book(self.user1_id, self.book1_id)

        # Sprawdź, czy wypożyczenie zostało utworzone
        self.assertIn(loan_id, self.loan_manager.loans)
        loan = self.loan_manager.get_loan(loan_id)
        self.assertEqual(loan["user_id"], self.user1_id)
        self.assertEqual(loan["book_id"], self.book1_id)
        self.assertEqual(loan["returned"], False)

        # Sprawdź, czy status książki zmienił się na niedostępny
        book = self.book_manager.get_book(self.book1_id)
        self.assertEqual(book["available"], False)

        # 2. Użytkownik zwraca książkę
        result = self.loan_manager.return_book(loan_id)
        self.assertTrue(result)

        # Sprawdź, czy wypożyczenie zostało oznaczone jako zwrócone
        loan = self.loan_manager.get_loan(loan_id)
        self.assertEqual(loan["returned"], True)

        # Sprawdź, czy status książki zmienił się na dostępny
        book = self.book_manager.get_book(self.book1_id)
        self.assertEqual(book["available"], True)

    def test_wypozyczenie_niedostepnej_ksiazki(self):
        """Test integracyjny próby wypożyczenia niedostępnej książki."""
        # 1. Użytkownik1 wypożycza książkę
        loan_id = self.loan_manager.loan_book(self.user1_id, self.book1_id)

        # 2. Użytkownik2 próbuje wypożyczyć tę samą książkę
        with self.assertRaises(ValueError) as context:
            self.loan_manager.loan_book(self.user2_id, self.book1_id)

        self.assertIn("jest już wypożyczona", str(context.exception))

        # 3. Użytkownik1 zwraca książkę
        self.loan_manager.return_book(loan_id)

        # 4. Teraz Użytkownik2 może wypożyczyć książkę
        loan_id2 = self.loan_manager.loan_book(self.user2_id, self.book1_id)
        self.assertIn(loan_id2, self.loan_manager.loans)

    def test_rezerwacja_i_wypozyczenie(self):
        """Test integracyjny rezerwacji i wypożyczenia książki."""
        # 1. Użytkownik1 wypożycza książkę
        loan_id = self.loan_manager.loan_book(self.user1_id, self.book1_id)

        # 2. Użytkownik2 rezerwuje tę samą książkę
        reservation_id = self.reservation_manager.reserve_book(self.user2_id, self.book1_id)

        # Sprawdź, czy rezerwacja została utworzona
        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["user_id"], self.user2_id)
        self.assertEqual(reservation["book_id"], self.book1_id)
        self.assertEqual(reservation["status"], "waiting")

        # 3. Użytkownik1 zwraca książkę
        self.loan_manager.return_book(loan_id)

        # 4. System powiadamia o dostępności książki dla Użytkownika2
        next_reservation_id = self.reservation_manager.book_returned(self.book1_id)
        self.assertEqual(next_reservation_id, reservation_id)

        # Sprawdź, czy status rezerwacji zmienił się na "ready"
        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["status"], "ready")
        self.assertTrue(reservation["notification_sent"])
        self.assertIn("expiry_date", reservation)

        # 5. Użytkownik2 wypożycza zarezerwowaną książkę
        loan_id2 = self.loan_manager.loan_book(self.user2_id, self.book1_id)

        # 6. Rezerwacja jest oznaczana jako zrealizowana
        self.reservation_manager.complete_reservation(reservation_id)

        # Sprawdź, czy status rezerwacji zmienił się na "completed"
        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["status"], "completed")

    def test_kategorie_i_wyszukiwanie(self):
        """Test integracyjny kategorii i wyszukiwania książek."""
        # 1. Dodaj nową kategorię
        self.category_manager.add_category("Przygodowe")

        # 2. Przypisz kilka kategorii do jednej książki
        self.category_manager.assign_category(self.book1_id, "Przygodowe")

        # Sprawdź, czy książka ma obie kategorie
        book = self.book_manager.get_book(self.book1_id)
        self.assertIn("Fantastyka", book["categories"])
        self.assertIn("Przygodowe", book["categories"])

        # 3. Wyszukaj książki w kategorii "Fantastyka"
        books_fantasy = self.category_manager.get_books_by_category("Fantastyka")
        self.assertIn(self.book1_id, books_fantasy)

        # 4. Wyszukaj książki w kategorii "Przygodowe"
        books_adventure = self.category_manager.get_books_by_category("Przygodowe")
        self.assertIn(self.book1_id, books_adventure)

        # 5. Usuń kategorię z książki
        self.category_manager.remove_category_from_book(self.book1_id, "Przygodowe")

        # Sprawdź, czy kategoria została usunięta
        book = self.book_manager.get_book(self.book1_id)
        self.assertNotIn("Przygodowe", book["categories"])

        # 6. Usuń całą kategorię
        self.category_manager.remove_category("Przygodowe")

        # Sprawdź, czy kategoria została usunięta z systemu
        categories = self.category_manager.get_all_categories()
        self.assertNotIn("Przygodowe", categories)

    def test_wygasniecie_rezerwacji(self):
        """Test integracyjny wygaśnięcia rezerwacji."""
        # 1. Użytkownik1 wypożycza książkę
        loan_id = self.loan_manager.loan_book(self.user1_id, self.book1_id)

        # 2. Użytkownik2 rezerwuje tę samą książkę
        reservation_id = self.reservation_manager.reserve_book(self.user2_id, self.book1_id)

        # 3. Użytkownik1 zwraca książkę
        self.loan_manager.return_book(loan_id)
        self.reservation_manager.book_returned(self.book1_id)

        # 4. Ręcznie ustaw datę wygaśnięcia na przeszłość
        reservation = self.reservation_manager.get_reservation(reservation_id)
        expiry_date = datetime.now() - timedelta(days=1)
        reservation["expiry_date"] = expiry_date.isoformat()

        # 5. Sprawdź wygasłe rezerwacje
        expired = self.reservation_manager.check_expired_reservations()

        # Sprawdź, czy rezerwacja została oznaczona jako wygasła
        self.assertIn(reservation_id, expired)

        # Sprawdź, czy status rezerwacji zmienił się na "expired"
        reservation = self.reservation_manager.get_reservation(reservation_id)
        self.assertEqual(reservation["status"], "expired")

        # 6. Sprawdź, czy książka jest ponownie dostępna
        book = self.book_manager.get_book(self.book1_id)
        self.assertEqual(book["available"], True)

    def test_kolejka_rezerwacji(self):
        """Test integracyjny kolejki rezerwacji."""
        # 1. Użytkownik1 wypożycza książkę
        loan_id = self.loan_manager.loan_book(self.user1_id, self.book1_id)

        # 2. Dodaj trzeciego użytkownika
        user3_id = self.user_manager.add_user("Piotr Nowicki", "piotr.nowicki@example.com")

        # 3. Użytkownik2 rezerwuje książkę
        reservation_id1 = self.reservation_manager.reserve_book(self.user2_id, self.book1_id)

        # 4. Użytkownik3 również rezerwuje książkę
        reservation_id2 = self.reservation_manager.reserve_book(user3_id, self.book1_id)

        # 5. Sprawdź pozycje w kolejce
        position1 = self.reservation_manager.get_position_in_queue(reservation_id1)
        position2 = self.reservation_manager.get_position_in_queue(reservation_id2)

        self.assertEqual(position1, 1)  # Użytkownik2 powinien być pierwszy w kolejce
        self.assertEqual(position2, 2)  # Użytkownik3 powinien być drugi w kolejce

        # 6. Użytkownik1 zwraca książkę
        self.loan_manager.return_book(loan_id)
        next_reservation_id = self.reservation_manager.book_returned(self.book1_id)

        # Sprawdź, czy to rezerwacja Użytkownika2 została wybrana jako następna
        self.assertEqual(next_reservation_id, reservation_id1)

        # 7. Użytkownik2 anuluje rezerwację
        self.reservation_manager.cancel_reservation(reservation_id1)

        # 8. Sprawdź, czy Użytkownik3 jest teraz pierwszy w kolejce
        position2_new = self.reservation_manager.get_position_in_queue(reservation_id2)
        self.assertEqual(position2_new, 1)

        # 9. Oznacz książkę jako ponownie dostępną i sprawdź powiadomienie
        book = self.book_manager.get_book(self.book1_id)
        book["available"] = True  # Symuluj dostępność książki
        next_reservation_id = self.reservation_manager.book_returned(self.book1_id)

        # Sprawdź, czy to rezerwacja Użytkownika3 została wybrana jako następna
        self.assertEqual(next_reservation_id, reservation_id2)

    def test_aktualizacja_danych(self):
        """Test integracyjny aktualizacji danych książek i użytkowników."""
        # 1. Aktualizuj dane książki
        self.book_manager.update_book(self.book1_id, new_title="Hobbit", new_author="J.R.R. Tolkien", new_year=1937)

        # Sprawdź, czy dane zostały zaktualizowane
        book = self.book_manager.get_book(self.book1_id)
        self.assertEqual(book["title"], "Hobbit")
        self.assertEqual(book["year"], 1937)

        # 2. Aktualizuj dane użytkownika
        self.user_manager.update_user(self.user1_id, new_name="Jan Nowak", new_email="jan.nowak@example.com")

        # Sprawdź, czy dane zostały zaktualizowane
        user = self.user_manager.get_user(self.user1_id)
        self.assertEqual(user["name"], "Jan Nowak")
        self.assertEqual(user["email"], "jan.nowak@example.com")

        # 3. Wypożycz książkę i sprawdź, czy zmiany są widoczne w wypożyczeniu
        loan_id = self.loan_manager.loan_book(self.user1_id, self.book1_id)
        loan = self.loan_manager.get_loan(loan_id)

        # Pobierz powiązane dane książki i użytkownika
        user = self.user_manager.get_user(loan["user_id"])
        book = self.book_manager.get_book(loan["book_id"])

        # Sprawdź, czy dane są aktualne
        self.assertEqual(user["name"], "Jan Nowak")
        self.assertEqual(book["title"], "Hobbit")

    def test_walidacja_danych(self):
        """Test integracyjny walidacji danych z użyciem utils."""
        # 1. Walidacja adresu email
        self.assertTrue(utils.validate_email("test@example.com"))
        self.assertFalse(utils.validate_email("test@example"))

        # 2. Walidacja ISBN
        self.assertTrue(utils.validate_isbn("1234567890"))
        self.assertTrue(utils.validate_isbn("1234567890123"))
        self.assertFalse(utils.validate_isbn("12345"))

        # 3. Walidacja ID użytkownika
        self.assertTrue(utils.validate_user_id(1))
        self.assertTrue(utils.validate_user_id(100))
        self.assertFalse(utils.validate_user_id(0))
        self.assertFalse(utils.validate_user_id(-1))

        # 4. Użyj walidacji w kontekście dodawania nowej książki
        valid_isbn = "1234567890"
        invalid_isbn = "123"

        # Sprawdź, czy valid_isbn jest prawidłowy
        self.assertTrue(utils.validate_isbn(valid_isbn))

        # Dodaj książkę z prawidłowym ISBN
        book_id = self.book_manager.add_book("Testowa książka", "Autor Testowy", valid_isbn)
        self.assertIn(book_id, self.book_manager.books)

        # Sprawdź, czy invalid_isbn jest nieprawidłowy
        self.assertFalse(utils.validate_isbn(invalid_isbn))

    def test_zapisywanie_i_wczytywanie_danych(self):
        """Test integracyjny zapisywania i wczytywania danych z pliku JSON."""
        # Przygotuj dane testowe
        test_data = {
            "books": self.book_manager.books,
            "users": self.user_manager.users,
            "loans": self.loan_manager.loans,
            "reservations": self.reservation_manager.reservations
        }

        # 1. Zapisz dane do pliku tymczasowego
        test_file_path = "test_data.json"
        utils.save_data(test_data, test_file_path)

        # 2. Wczytaj dane z pliku
        loaded_data = utils.load_data(test_file_path)

        # 3. Sprawdź, czy dane są identyczne
        self.assertEqual(loaded_data["books"], self.book_manager.books)
        self.assertEqual(loaded_data["users"], self.user_manager.users)
        self.assertEqual(loaded_data["loans"], self.loan_manager.loans)
        self.assertEqual(loaded_data["reservations"], self.reservation_manager.reservations)

        # Usuń plik testowy po zakończeniu testu
        if os.path.exists(test_file_path):
            os.remove(test_file_path)


if __name__ == '__main__':
    unittest.main()