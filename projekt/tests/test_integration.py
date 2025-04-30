import unittest
import os
import json
from src.user_manager import UserManager
from src.book_manager import BookManager
from src.loan_manager import LoanManager
from src.utils import save_data, load_data
from src.category_manager import CategoryManager
from src.reservation_manager import ReservationManager


class TestIntegracyjny(unittest.TestCase):
    """Testy integracyjne dla systemu zarządzania biblioteką."""

    def setUp(self):
        """Tworzenie nowych instancji managerów przed każdym testem."""
        self.user_manager = UserManager()
        self.book_manager = BookManager()
        self.loan_manager = LoanManager(self.book_manager, self.user_manager)

        # Dodanie przykładowych danych do testów
        self.user_id = self.user_manager.add_user("Jan Kowalski", "jan@example.com")
        self.book_id = self.book_manager.add_book("Wiedźmin", "Andrzej Sapkowski", "1234567890")

    def tearDown(self):
        """Czyszczenie po testach - usuwanie plików testowych."""
        test_files = ['test_users.json', 'test_books.json', 'test_loans.json']
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)

    def test_wypozyczenie_ksiazki(self):
        """Test procesu wypożyczenia książki."""
        # Wypożyczenie książki
        loan_id = self.loan_manager.loan_book(self.user_id, self.book_id)

        # Sprawdzenie czy wypożyczenie zostało zarejestrowane
        loan = self.loan_manager.get_loan(loan_id)
        self.assertEqual(loan["user_id"], self.user_id)
        self.assertEqual(loan["book_id"], self.book_id)
        self.assertFalse(loan["returned"])

        # Sprawdzenie czy książka jest oznaczona jako niedostępna
        book = self.book_manager.get_book(self.book_id)
        self.assertFalse(book["available"])

    def test_zwrot_ksiazki(self):
        """Test procesu zwrotu książki."""
        # Wypożyczenie a następnie zwrot książki
        loan_id = self.loan_manager.loan_book(self.user_id, self.book_id)
        self.loan_manager.return_book(loan_id)

        # Sprawdzenie czy wypożyczenie zostało oznaczone jako zwrócone
        loan = self.loan_manager.get_loan(loan_id)
        self.assertTrue(loan["returned"])

        # Sprawdzenie czy książka jest ponownie dostępna
        book = self.book_manager.get_book(self.book_id)
        self.assertTrue(book["available"])

    def test_wiele_wypozyczen(self):
        """Test obsługi wielu wypożyczeń."""
        # Dodanie kilku użytkowników i książek
        user_id2 = self.user_manager.add_user("Anna Nowak", "anna@example.com")
        book_id2 = self.book_manager.add_book("Harry Potter", "J.K. Rowling", "0987654321")

        # Kilka wypożyczeń
        loan_id1 = self.loan_manager.loan_book(self.user_id, self.book_id)
        loan_id2 = self.loan_manager.loan_book(user_id2, book_id2)

        # Sprawdzenie czy wszystkie wypożyczenia są zarejestrowane
        self.assertEqual(len(self.loan_manager.loans), 2)

        # Zwrot jednej książki
        self.loan_manager.return_book(loan_id1)

        # Sprawdzenie statusu książek
        book1 = self.book_manager.get_book(self.book_id)
        book2 = self.book_manager.get_book(book_id2)
        self.assertTrue(book1["available"])
        self.assertFalse(book2["available"])

    def test_niedostepna_ksiazka(self):
        """Test próby wypożyczenia niedostępnej książki."""
        # Wypożyczenie książki
        self.loan_manager.loan_book(self.user_id, self.book_id)

        # Próba ponownego wypożyczenia tej samej książki
        with self.assertRaises(ValueError):
            self.loan_manager.loan_book(self.user_id, self.book_id)

    def test_nieistniejacy_uzytkownik(self):
        """Test próby wypożyczenia książki przez nieistniejącego użytkownika."""
        with self.assertRaises(ValueError):
            self.loan_manager.loan_book(999, self.book_id)

    def test_nieistniejaca_ksiazka(self):
        """Test próby wypożyczenia nieistniejącej książki."""
        with self.assertRaises(ValueError):
            self.loan_manager.loan_book(self.user_id, 999)

    def test_podwojny_zwrot_ksiazki(self):
        """Test próby zwrotu już zwróconej książki."""
        loan_id = self.loan_manager.loan_book(self.user_id, self.book_id)
        self.loan_manager.return_book(loan_id)

        # Próba ponownego zwrotu
        with self.assertRaises(ValueError):
            self.loan_manager.return_book(loan_id)

    def test_zapis_i_odczyt_danych(self):
        """Test zapisywania i odczytywania danych."""
        # Wypożyczenie książki
        loan_id = self.loan_manager.loan_book(self.user_id, self.book_id)

        # Zapis danych
        save_data(self.user_manager.users, 'test_users.json')
        save_data(self.book_manager.books, 'test_books.json')
        save_data(self.loan_manager.loans, 'test_loans.json')

        # Odczyt danych
        loaded_users = load_data('test_users.json')
        loaded_books = load_data('test_books.json')
        loaded_loans = load_data('test_loans.json')

        # Sprawdzenie czy dane zostały poprawnie zapisane i odczytane
        self.assertTrue(
            str(self.user_id) in str(loaded_users))  # Sprawdza czy ID użytkownika istnieje w załadowanych danych
        self.assertTrue(
            str(self.book_id) in str(loaded_books))  # Sprawdza czy ID książki istnieje w załadowanych danych
        self.assertTrue(
            str(loan_id) in str(loaded_loans))  # Sprawdza czy ID wypożyczenia istnieje w załadowanych danych

    def test_aktualizacja_danych(self):
        """Test aktualizacji danych użytkownika i książki."""
        # Aktualizacja danych użytkownika
        self.user_manager.update_user(self.user_id, new_name="Jan Nowak", new_email="jan.nowak@example.com")
        user = self.user_manager.get_user(self.user_id)
        self.assertEqual(user["name"], "Jan Nowak")
        self.assertEqual(user["email"], "jan.nowak@example.com")

        # Aktualizacja danych książki
        self.book_manager.update_book(self.book_id, new_title="Wiedźmin: Ostatnie życzenie", new_author="A. Sapkowski",
                                      new_year=1993)
        book = self.book_manager.get_book(self.book_id)
        self.assertEqual(book["title"], "Wiedźmin: Ostatnie życzenie")
        self.assertEqual(book["author"], "A. Sapkowski")
        self.assertEqual(book["year"], 1993)

    def test_wyszukiwanie(self):
        """Test wyszukiwania użytkowników i książek."""
        # Dodanie kilku użytkowników i książek
        self.user_manager.add_user("Jan Nowak", "jan.nowak@example.com")
        self.user_manager.add_user("Janina Kowalska", "janina@example.com")

        self.book_manager.add_book("Hobbit", "J.R.R. Tolkien", "1122334455")
        self.book_manager.add_book("Wiedźmin: Krew elfów", "Andrzej Sapkowski", "5566778899")

        # Wyszukiwanie użytkowników
        users_jan = self.user_manager.find_users_by_name("Jan")
        self.assertEqual(len(users_jan), 3)  # Jan Kowalski, Jan Nowak i Janina Kowalska

        # Wyszukiwanie książek
        books_wiedźmin = self.book_manager.find_books_by_title("Wiedźmin")
        self.assertEqual(len(books_wiedźmin), 2)  # Wiedźmin i Wiedźmin: Krew elfów

        books_sapkowski = self.book_manager.find_books_by_author("Sapkowski")
        self.assertEqual(len(books_sapkowski), 2)  # Wiedźmin i Wiedźmin: Krew elfów




if __name__ == '__main__':
    unittest.main()