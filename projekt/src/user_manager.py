
class UserManager:
    def __init__(self):
        self.users = {}  # słownik z ID jako kluczami
        self.next_id = 1  # zaczynamy od ID=1

    def add_user(self, name, email):
        if not name or not isinstance(name, str):
            raise ValueError("Imię musi być niepustym ciągiem znaków")
        if not email or not isinstance(email, str):
            raise ValueError("Email musi być niepustym ciągiem znaków")
        if len(name) > 200:  # limit długości imienia
            raise ValueError("Imię jest zbyt długie")

        user = {
            "name": name,
            "email": email
        }

        user_id = self.next_id
        self.users[user_id] = user
        self.next_id += 1

        return user_id

    def remove_user(self, user_id):
        if user_id not in self.users:
            raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")
        del self.users[user_id]

    def get_user(self, user_id):
        if user_id not in self.users:
            raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")
        return self.users[user_id]

    def find_users_by_name(self, name):
        return [user for user_id, user in self.users.items()
                if name.lower() in user["name"].lower()]

    def update_user(self, user_id, new_name=None, new_email=None):
        if user_id not in self.users:
            raise ValueError(f"Użytkownik o ID {user_id} nie istnieje")

        user = self.users[user_id]

        if new_name:
            if not isinstance(new_name, str) or len(new_name) == 0:
                raise ValueError("Imię musi być niepustym ciągiem znaków")
            user["name"] = new_name

        if new_email:
            if not isinstance(new_email, str) or len(new_email) == 0:
                raise ValueError("Email musi być niepustym ciągiem znaków")
            user["email"] = new_email

        return True

    def list_users(self):
        return list(self.users.values())
