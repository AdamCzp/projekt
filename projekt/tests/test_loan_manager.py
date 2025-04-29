import pytest
from src.loan_manager import LoanManager
from src.book_manager import BookManager
from src.user_manager import UserManager


@pytest.fixture
def setup_managers():
    book_manager = BookManager()
    user_manager = UserManager()
    loan_manager = LoanManager(book_manager, user_manager)
    # Dodaj ISBN jako trzeci argument
    book_id = book_manager.add_book("1984", "George Orwell", "9780451524935", 1949)
    user_id = user_manager.add_user("John Doe", "john@example.com")
    return loan_manager, book_id, user_id, book_manager, user_manager


class TestLoanBook:
    def test_loan_book_success(self, setup_managers):
        loan_manager, book_id, user_id, *_ = setup_managers
        loan_id = loan_manager.loan_book(user_id, book_id)
        assert loan_id == 1
        assert loan_manager.loans[loan_id]["user_id"] == user_id
        assert loan_manager.loans[loan_id]["book_id"] == book_id
        assert loan_manager.book_manager.get_book(book_id)["available"] is False

    @pytest.mark.parametrize("user_id,book_id", [
        (999, 1),  # nieistniejący użytkownik
        (1, 999),  # nieistniejąca książka
    ])
    def test_loan_book_invalid_ids(self, setup_managers, user_id, book_id):
        loan_manager, _, _, *_ = setup_managers
        with pytest.raises(ValueError):
            loan_manager.loan_book(user_id, book_id)

    def test_loan_already_loaned_book(self, setup_managers):
        loan_manager, book_id, user_id, *_ = setup_managers
        loan_manager.loan_book(user_id, book_id)
        with pytest.raises(ValueError):
            loan_manager.loan_book(user_id, book_id)


class TestReturnBook:
    def test_return_book_success(self, setup_managers):
        loan_manager, book_id, user_id, *_ = setup_managers
        loan_id = loan_manager.loan_book(user_id, book_id)
        loan_manager.return_book(loan_id)
        assert loan_manager.loans[loan_id]["returned"] is True
        assert loan_manager.book_manager.get_book(book_id)["available"] is True

    def test_return_book_nonexistent(self, setup_managers):
        loan_manager, *_ = setup_managers
        with pytest.raises(ValueError):
            loan_manager.return_book(999)

    def test_return_book_already_returned(self, setup_managers):
        loan_manager, book_id, user_id, *_ = setup_managers
        loan_id = loan_manager.loan_book(user_id, book_id)
        loan_manager.return_book(loan_id)
        with pytest.raises(ValueError):
            loan_manager.return_book(loan_id)


class TestGetLoan:
    def test_get_loan_success(self, setup_managers):
        loan_manager, book_id, user_id, *_ = setup_managers
        loan_id = loan_manager.loan_book(user_id, book_id)
        loan = loan_manager.get_loan(loan_id)
        assert isinstance(loan, dict)
        assert loan["user_id"] == user_id
        assert loan["book_id"] == book_id

    def test_get_loan_nonexistent(self, setup_managers):
        loan_manager, *_ = setup_managers
        with pytest.raises(ValueError):
            loan_manager.get_loan(123)


class TestListLoans:
    def test_list_loans_empty(self, setup_managers):
        loan_manager, *_ = setup_managers
        loans = loan_manager.list_loans()
        assert loans == []

    def test_list_loans_single(self, setup_managers):
        loan_manager, book_id, user_id, *_ = setup_managers
        loan_manager.loan_book(user_id, book_id)
        loans = loan_manager.list_loans()
        assert len(loans) == 1
        assert loans[0]["user_id"] == user_id

    def test_list_loans_multiple(self, setup_managers):
        loan_manager, book_id, user_id, book_manager, user_manager = setup_managers
        # Dodaj ISBN jako trzeci argument
        book_id2 = book_manager.add_book("Animal Farm", "George Orwell", "9780451526342", 1945)
        user_id2 = user_manager.add_user("Jane Doe", "jane@example.com")
        loan_manager.loan_book(user_id, book_id)
        loan_manager.loan_book(user_id2, book_id2)
        loans = loan_manager.list_loans()
        assert len(loans) == 2
        user_ids = [loan["user_id"] for loan in loans]
        assert user_id in user_ids
        assert user_id2 in user_ids


class TestComplexLoanScenarios:
    def test_multiple_loans_same_user(self, setup_managers):
        loan_manager, book_id, user_id, book_manager, *_ = setup_managers
        # Dodaj ISBN jako trzeci argument
        book_id2 = book_manager.add_book("Brave New World", "Aldous Huxley", "9780060850524", 1932)
        loan_manager.loan_book(user_id, book_id)
        loan_manager.loan_book(user_id, book_id2)
        loans = loan_manager.list_loans()
        assert len(loans) == 2
        for loan in loans:
            assert loan["user_id"] == user_id

    def test_cannot_loan_returned_book_immediately(self, setup_managers):
        loan_manager, book_id, user_id, *_ = setup_managers
        loan_id = loan_manager.loan_book(user_id, book_id)
        loan_manager.return_book(loan_id)
        new_loan_id = loan_manager.loan_book(user_id, book_id)
        assert new_loan_id != loan_id

    def test_user_and_book_state_after_loan_and_return(self, setup_managers):
        loan_manager, book_id, user_id, *_ = setup_managers
        loan_id = loan_manager.loan_book(user_id, book_id)
        loan_manager.return_book(loan_id)
        book = loan_manager.book_manager.get_book(book_id)
        assert book["available"] is True
        loan = loan_manager.get_loan(loan_id)
        assert loan["returned"] is True