import unittest
from src.category_manager import CategoryManager  # zakładamy, że klasa jest w pliku category_manager.py

# Dummy BookManager
class DummyBookManager:
    def __init__(self):
        self.books = {}

    def add_book(self, book_id):
        self.books[book_id] = {"id": book_id, "categories": []}

    def get_book(self, book_id):
        if book_id not in self.books:
            raise ValueError("Book not found")
        return self.books[book_id]

class TestCategoryManager(unittest.TestCase):
    def setUp(self):
        self.book_manager = DummyBookManager()
        self.category_manager = CategoryManager(self.book_manager)

        self.book_manager.add_book(1)
        self.book_manager.add_book(2)

    def test_add_category(self):
        self.category_manager.add_category("Fantasy")
        self.assertIn("Fantasy", self.category_manager.get_all_categories())

    def test_add_existing_category(self):
        self.category_manager.add_category("Fantasy")
        with self.assertRaises(ValueError):
            self.category_manager.add_category("Fantasy")

    def test_remove_category(self):
        self.category_manager.add_category("Sci-Fi")
        self.category_manager.remove_category("Sci-Fi")
        self.assertNotIn("Sci-Fi", self.category_manager.get_all_categories())

    def test_remove_nonexistent_category(self):
        with self.assertRaises(ValueError):
            self.category_manager.remove_category("Horror")

    def test_assign_category_to_book(self):
        self.category_manager.add_category("History")
        self.category_manager.assign_category(1, "History")
        book = self.book_manager.get_book(1)
        self.assertIn("History", book["categories"])

    def test_assign_nonexistent_category(self):
        with self.assertRaises(ValueError):
            self.category_manager.assign_category(1, "Unknown")

    def test_assign_to_nonexistent_book(self):
        self.category_manager.add_category("Science")
        with self.assertRaises(ValueError):
            self.category_manager.assign_category(999, "Science")

    def test_remove_category_from_book(self):
        self.category_manager.add_category("Drama")
        self.category_manager.assign_category(1, "Drama")
        self.category_manager.remove_category_from_book(1, "Drama")
        self.assertNotIn("Drama", self.book_manager.get_book(1)["categories"])

    def test_get_books_by_category(self):
        self.category_manager.add_category("Adventure")
        self.category_manager.assign_category(1, "Adventure")
        self.category_manager.assign_category(2, "Adventure")
        result = self.category_manager.get_books_by_category("Adventure")
        self.assertCountEqual(result, [1, 2])

    def test_get_books_by_nonexistent_category(self):
        with self.assertRaises(ValueError):
            self.category_manager.get_books_by_category("Nonexistent")

if __name__ == "__main__":
    unittest.main()
