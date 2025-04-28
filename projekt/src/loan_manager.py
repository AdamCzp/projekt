class LoanManager:
    def __init__(self):
        self.loans = []  # lista wypożyczeń: każdy element to słownik {"user_id", "isbn"}

    def borrow_book(self, user_id, isbn):
        """Użytkownik wypożycza książkę."""
        if self.is_book_borrowed(isbn):
            return False  # książka już wypożyczona
        loan = {
            "user_id": user_id,
            "isbn": isbn
        }
        self.loans.append(loan)
        return True

    def return_book(self, isbn):
        """Użytkownik oddaje książkę."""
        for loan in self.loans:
            if loan["isbn"] == isbn:
                self.loans.remove(loan)
                return True
        return False  # książka nie była wypożyczona

    def is_book_borrowed(self, isbn):
        """Sprawdza, czy książka jest obecnie wypożyczona."""
        for loan in self.loans:
            if loan["isbn"] == isbn:
                return True
        return False

    def list_all_loans(self):
        """Zwraca listę wszystkich aktywnych wypożyczeń."""
        return self.loans