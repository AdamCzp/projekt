# System Zarządzania Biblioteką

Prosty, modułowy system do zarządzania biblioteką napisany w Pythonie, z pełnym zestawem testów jednostkowych i integracyjnych.

## Spis treści

- [Opis projektu](#opis-projektu)  
- [Funkcjonalności](#funkcjonalności)  
- [Struktura katalogów](#struktura-katalogów)  
- [Instalacja](#instalacja)  
- [Uruchamianie aplikacji](#uruchamianie-aplikacji)  
- [Testy](#testy)  
- [Przykłady użycia](#przykłady-użycia)  
- [Contributing](#contributing)  
- [Licencja](#licencja)  

---

## Opis projektu

Ten projekt implementuje podstawowy “System Zarządzania Biblioteką” z następującymi modułami:

- **UserManager** — tworzenie, odczyt, aktualizacja i usuwanie użytkowników.  
- **BookManager** — zarządzanie książkami: dodawanie, wyszukiwanie, aktualizacja, usuwanie.  
- **LoanManager** — obsługa wypożyczeń i zwrotów książek, razem z walidacją dostępności.  
- **ReservationManager** — kolejkowanie rezerwacji, powiadamianie, wygasanie i realizacja.  
- **CategoryManager** — tworzenie kategorii, przypisywanie ich do książek, wyszukiwanie po kategoriach.  
- **Utils** — pomocnicze funkcje do zapisu/odczytu JSON.

Kod został napisany zgodnie z PEP 8, z obsługą wyjątków i bez obowiązkowego type hintingu.

---

## Funkcjonalności

1. **Zarządzanie użytkownikami**  
   - `add_user(name, email) → user_id`  
   - `get_user(user_id) → dict`  
   - `update_user(user_id, new_name, new_email)`  
   - `remove_user(user_id)`  
   - `find_users_by_name(substring) → list[dict]`  

2. **Zarządzanie książkami**  
   - `add_book(title, author, isbn, year=None) → book_id`  
   - `get_book(book_id) → dict`  
   - `update_book(book_id, new_title, new_author, new_year)`  
   - `remove_book(book_id)`  
   - `find_books_by_title(substring) → list[dict]`  
   - `find_books_by_author(substring) → list[dict]`  

3. **Wypożyczenia**  
   - `loan_book(user_id, book_id) → loan_id`  
   - `return_book(loan_id)`  
   - `get_loan(loan_id) → dict`  
   - `list_loans() → list[dict]`  

4. **Rezerwacje**  
   - `reserve_book(user_id, book_id) → reservation_id`  
   - `cancel_reservation(reservation_id)`  
   - `book_returned(book_id) → next_reservation_id or False`  
   - `check_expired_reservations() → list[reservation_id]`  
   - `complete_reservation(reservation_id)`  
   - `get_position_in_queue(reservation_id) → int`  

5. **Kategorie**  
   - `add_category(name)`  
   - `remove_category(name)`  
   - `get_all_categories() → list[str]`  
   - `assign_category(book_id, name)`  
   - `remove_category_from_book(book_id, name)`  
   - `get_books_by_category(name) → list[book_id]`  

6. **Utils**  
   - `save_data(data: dict, path: str)` — zapis JSON  
   - `load_data(path: str) → dict` — odczyt JSON  

---

## Struktura katalogów

```

projekt/
├── src/
│   ├── **init**.py
│   ├── book\_manager.py
│   ├── user\_manager.py
│   ├── loan\_manager.py
│   ├── reservation\_manager.py
│   ├── category\_manager.py
│   └── utils.py
├── tests/
│   ├── **init**.py
│   ├── test\_book\_manager.py
│   ├── test\_user\_manager.py
│   ├── test\_loan\_manager.py
│   ├── test\_reservation\_manager.py
│   ├── test\_category\_manager.py
│   ├── test\_utils.py
│   └── test\_integration.py
├── requirements.txt
└── README.md

````

---

## Instalacja

1. Sklonuj repozytorium i przejdź do katalogu:
   ```bash
   git clone https://github.com/AdamCzp/projekt.git
   cd projekt
````

2. (Opcjonalnie) Utwórz i aktywuj wirtualne środowisko:

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. Zainstaluj zależności:

   ```bash
   pip install -r requirements.txt
   ```

---

## Uruchamianie aplikacji

To jest biblioteka Pythonowa, nie ma interfejsu CLI; importuj moduły w swoim skrypcie:

```python
from src.user_manager import UserManager
from src.book_manager import BookManager
from src.loan_manager import LoanManager

um = UserManager()
bm = BookManager()
lm = LoanManager(bm, um)

uid = um.add_user("Jan Kowalski", "jan@example.com")
bid = bm.add_book("Wiedźmin", "Andrzej Sapkowski", "1234567890", year=1993)
loan = lm.loan_book(uid, bid)
```

---

## Testy

Uruchom wszystkie testy:

```bash
pytest
```

Pokrycie kodu:

```bash
pytest --cov=src --cov-report=term-missing
```

lub:

```bash
python -m coverage run -m pytest
python -m coverage report -m
```

---

## Licencja

Ten projekt jest objęty licencją **MIT**.

```


