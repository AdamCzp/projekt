class UserManager:
    def __init__(self):
        self.users = []  # lista słowników, każdy słownik to użytkownik

    def add_user(self, user_id, first_name, last_name, email):
        """Dodaje nowego użytkownika."""
        user = {
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email
        }
        self.users.append(user)

    def remove_user(self, user_id):
        """Usuwa użytkownika na podstawie ID."""
        for user in self.users:
            if user["user_id"] == user_id:
                self.users.remove(user)
                return True
        return False  # nie znaleziono

    def find_user_by_id(self, user_id):
        """Zwraca użytkownika na podstawie ID."""
        for user in self.users:
            if user["user_id"] == user_id:
                return user
        return None

    def find_users_by_name(self, name):
        """Zwraca listę użytkowników zawierających imię lub nazwisko."""
        return [
            user for user in self.users
            if name.lower() in user["first_name"].lower() or name.lower() in user["last_name"].lower()
        ]

    def update_user(self, user_id, new_first_name=None, new_last_name=None, new_email=None):
        """Aktualizuje dane użytkownika."""
        for user in self.users:
            if user["user_id"] == user_id:
                if new_first_name:
                    user["first_name"] = new_first_name
                if new_last_name:
                    user["last_name"] = new_last_name
                if new_email:
                    user["email"] = new_email
                return True
        return False

    def list_all_users(self):
        """Zwraca listę wszystkich użytkowników."""
        return self.users
