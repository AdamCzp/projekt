import re

def validate_email(email):
    """Sprawdza, czy adres e-mail jest poprawny."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_isbn(isbn):
    """Sprawdza, czy ISBN składa się z 10 lub 13 cyfr."""
    return isbn.isdigit() and len(isbn) in (10, 13)

def validate_user_id(user_id):
    """Sprawdza, czy ID użytkownika jest liczbą całkowitą większą od zera."""
    return isinstance(user_id, int) and user_id > 0
