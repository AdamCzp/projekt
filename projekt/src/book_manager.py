class BookManager:
    def __init__(self):
        self.books = []  # lista słowników, każdy słownik to jedna książka

    def add_book(self, title, author, isbn, year):
        """Dodaje nową książkę."""
        book = {
            "title": title,
            "author": author,
            "isbn": isbn,
            "year": year
        }
        self.books.append(book)

    def remove_book(self, isbn):
        """Usuwa książkę na podstawie ISBN."""
        for book in self.books:
            if book["isbn"] == isbn:
                self.books.remove(book)
                return True
        return False  # nie znaleziono

    def find_books_by_title(self, title):
        """Zwraca listę książek zawierających tytuł."""
        return [book for book in self.books if title.lower() in book["title"].lower()]

    def find_books_by_author(self, author):
        """Zwraca listę książek zawierających autora."""
        return [book for book in self.books if author.lower() in book["author"].lower()]

    def update_book(self, isbn, new_title=None, new_author=None, new_year=None):
        """Aktualizuje dane książki."""
        for book in self.books:
            if book["isbn"] == isbn:
                if new_title:
                    book["title"] = new_title
                if new_author:
                    book["author"] = new_author
                if new_year:
                    book["year"] = new_year
                return True
        return False  # nie znaleziono

    def list_all_books(self):
        """Zwraca listę wszystkich książek."""
        return self.books
