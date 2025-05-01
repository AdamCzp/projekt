import pytest
from src.user_manager import UserManager


class TestAddUser:
    def test_add_user_success(self):
        manager = UserManager()
        user_id = manager.add_user("Alice", "alice@example.com")
        assert user_id == 1
        assert manager.users[user_id]["name"] == "Alice"
        assert manager.users[user_id]["email"] == "alice@example.com"

    @pytest.mark.parametrize(
        "name,email",
        [
            ("", "user@example.com"),
            ("User", ""),
            (None, "user@example.com"),
            ("User", None),
            ("U"*300, "user@example.com"),  # bardzo długie imię
            (123, "user@example.com"),       # imię jako liczba
            ("User", 456),                   # email jako liczba
        ]
    )
    def test_add_user_invalid_data(self, name, email):
        manager = UserManager()
        with pytest.raises(ValueError):
            manager.add_user(name, email)

    def test_add_multiple_users_unique_ids(self):
        manager = UserManager()
        id1 = manager.add_user("User One", "one@example.com")
        id2 = manager.add_user("User Two", "two@example.com")
        assert id1 != id2
        assert len(manager.users) == 2


class TestRemoveUser:
    def test_remove_user_success(self):
        manager = UserManager()
        user_id = manager.add_user("Bob", "bob@example.com")
        manager.remove_user(user_id)
        assert user_id not in manager.users

    def test_remove_user_nonexistent(self):
        manager = UserManager()
        with pytest.raises(ValueError):
            manager.remove_user(99)

    def test_remove_user_twice(self):
        manager = UserManager()
        user_id = manager.add_user("Bob", "bob@example.com")
        manager.remove_user(user_id)
        with pytest.raises(ValueError):
            manager.remove_user(user_id)


class TestGetUser:
    def test_get_user_success(self):
        manager = UserManager()
        user_id = manager.add_user("Charlie", "charlie@example.com")
        user = manager.get_user(user_id)
        assert isinstance(user, dict)
        assert user["name"] == "Charlie"

    def test_get_user_nonexistent(self):
        manager = UserManager()
        with pytest.raises(ValueError):
            manager.get_user(42)

    def test_get_user_after_removal(self):
        manager = UserManager()
        user_id = manager.add_user("Charlie", "charlie@example.com")
        manager.remove_user(user_id)
        with pytest.raises(ValueError):
            manager.get_user(user_id)


class TestListUsers:
    def test_list_users_empty(self):
        manager = UserManager()
        users = manager.list_users()
        assert users == []

    def test_list_users_single(self):
        manager = UserManager()
        manager.add_user("Dana", "dana@example.com")
        users = manager.list_users()
        assert len(users) == 1
        assert users[0]["name"] == "Dana"

    def test_list_users_multiple(self):
        manager = UserManager()
        names = ["Eve", "Frank", "Grace"]
        for name in names:
            manager.add_user(name, f"{name.lower()}@example.com")
        users = manager.list_users()
        assert len(users) == 3
        returned_names = [user["name"] for user in users]
        for name in names:
            assert name in returned_names
