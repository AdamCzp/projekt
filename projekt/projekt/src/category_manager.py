class CategoryManager:
    def __init__(self, book_manager):
        self.book_manager = book_manager
        self.categories = set()

    def add_category(self, category):
        if category in self.categories:
            raise ValueError("Category already exists")
        self.categories.add(category)

    def remove_category(self, category):
        if category not in self.categories:
            raise ValueError("Category does not exist")
        self.categories.remove(category)
        for book in self.book_manager.books.values():
            if category in book["categories"]:
                book["categories"].remove(category)

    def get_all_categories(self):
        return list(self.categories)

    def assign_category(self, book_id, category):
        if category not in self.categories:
            raise ValueError("Category does not exist")
        book = self.book_manager.get_book(book_id)
        if category not in book["categories"]:
            book["categories"].append(category)

    def remove_category_from_book(self, book_id, category):
        book = self.book_manager.get_book(book_id)
        if category in book["categories"]:
            book["categories"].remove(category)

    def get_books_by_category(self, category):
        if category not in self.categories:
            raise ValueError("Category does not exist")
        return [book_id for book_id, book in self.book_manager.books.items()
                if category in book["categories"]]
