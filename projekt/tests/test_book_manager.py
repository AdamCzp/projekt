import pytest
from src.book_manager import BookManager


class TestAddBook:
    def test_add_book_success(self):
        manager = BookManager()
        book_id = manager.add_book("The Hobbit", "J.R.R. Tolkien", "9780547928227", 1937)
        assert book_id == 1
        assert manager.books[book_id]["title"] == "The Hobbit"
        assert manager.books[book_id]["author"] == "J.R.R. Tolkien"
        assert manager.books[book_id]["isbn"] == "9780547928227"

    @pytest.mark.parametrize(
        "title,author,isbn",
        [
            ("", "Author", "1234567890"),
            ("Title", "", "1234567890"),
            ("Title", "Author", ""),
            (None, "Author", "1234567890"),
            ("Title", None, "1234567890"),
            ("Title", "Author", None),
            ("A"*300, "Author", "1234567890"),  # bardzo długi tytuł
            (123, "Author", "1234567890"),  # tytuł jako liczba
            ("Title", 456, "1234567890"),  # autor jako liczba
            ("Title", "Author", 789),  # ISBN jako liczba
        ]
    )
    @pytest.mark.parametrize(
        "title,author,isbn,year",
        [
            ("", "Author", "1234567890", 2000),
            ("Title", "", "1234567890", 2000),
            ("Title", "Author", "", 2000),
            (None, "Author", "1234567890", 2000),
            ("Title", None, "1234567890", 2000),
            ("Title", "Author", None, 2000),
            ("A" * 300, "Author", "1234567890", 2000),
            (123, "Author", "1234567890", 2000),
            ("Title", 456, "1234567890", 2000),
            ("Title", "Author", 789, 2000),
        ]
    )
    def test_add_book_invalid_data(self, title, author, isbn, year):
        manager = BookManager()
        with pytest.raises(ValueError):
            manager.add_book(title, author, isbn, year)

    def test_add_multiple_books_unique_ids(self):
        manager = BookManager()
        id1 = manager.add_book("Book One", "Author A", "1111111111")
        id2 = manager.add_book("Book Two", "Author B", "2222222222")
        assert id1 != id2
        assert len(manager.books) == 2


class TestRemoveBook:
    def test_remove_book_success(self):
        manager = BookManager()
        book_id = manager.add_book("Title", "Author", "1234567890")
        manager.remove_book(book_id)
        assert book_id not in manager.books

    def test_remove_book_nonexistent(self):
        manager = BookManager()
        with pytest.raises(ValueError):
            manager.remove_book(99)

    def test_remove_book_twice(self):
        manager = BookManager()
        book_id = manager.add_book("Title", "Author", "1234567890")
        manager.remove_book(book_id)
        with pytest.raises(ValueError):
            manager.remove_book(book_id)


class TestGetBook:
    def test_get_book_success(self):
        manager = BookManager()
        book_id = manager.add_book("Title", "Author", "1234567890")
        book = manager.get_book(book_id)
        assert isinstance(book, dict)
        assert book["title"] == "Title"

    def test_get_book_nonexistent(self):
        manager = BookManager()
        with pytest.raises(ValueError):
            manager.get_book(42)

    def test_get_book_after_removal(self):
        manager = BookManager()
        book_id = manager.add_book("Title", "Author", "1234567890")
        manager.remove_book(book_id)
        with pytest.raises(ValueError):
            manager.get_book(book_id)


class TestListBooks:
    def test_list_books_empty(self):
        manager = BookManager()
        books = manager.list_books()
        assert books == []

    def test_list_books_single(self):
        manager = BookManager()
        manager.add_book("Only Book", "Author", "9999999999")
        books = manager.list_books()
        assert len(books) == 1
        assert books[0]["title"] == "Only Book"

    def test_list_books_multiple(self):
        manager = BookManager()
        titles = ["Book A", "Book B", "Book C"]
        for title in titles:
            manager.add_book(title, "Author", "0000000000")
        books = manager.list_books()
        assert len(books) == 3
        returned_titles = [book["title"] for book in books]
        for title in titles:
            assert title in returned_titles
