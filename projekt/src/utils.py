import re
import json

def save_data(data, file_path):
    """Save data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data(file_path):
    """Load data from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
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
