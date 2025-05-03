
class LoanManager:
    def __init__(self, book_manager, user_manager):
        self.loans = {}
        self.next_id = 1
        self.book_manager = book_manager
        self.user_manager = user_manager

    def loan_book(self, user_id, book_id):
        try:
            self.user_manager.get_user(user_id)
        except ValueError:
            raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

        try:
            book = self.book_manager.get_book(book_id)
        except ValueError:
            raise ValueError(f"Książka o ID {book_id} nie istnieje")

        if book.get("available") is False:
            raise ValueError(f"Książka o ID {book_id} jest już wypożyczona")

        book["available"] = False

        loan = {
            "user_id": user_id,
            "book_id": book_id,
            "returned": False
        }

        loan_id = self.next_id
        self.loans[loan_id] = loan
        self.next_id += 1

        return loan_id

    def return_book(self, loan_id):
        if loan_id not in self.loans:
            raise ValueError(f"Wypożyczenie o ID {loan_id} nie istnieje")

        loan = self.loans[loan_id]

        if loan["returned"]:
            raise ValueError(f"Książka z wypożyczenia o ID {loan_id} została już zwrócona")

        loan["returned"] = True

        book = self.book_manager.get_book(loan["book_id"])
        book["available"] = True

        return True

    def get_loan(self, loan_id):
        if loan_id not in self.loans:
            raise ValueError(f"Wypożyczenie o ID {loan_id} nie istnieje")
        return self.loans[loan_id]

    def list_loans(self):
        return list(self.loans.values())
