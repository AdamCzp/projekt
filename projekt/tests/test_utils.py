import pytest
from src.utils import validate_email, validate_isbn, validate_user_id


class TestValidateEmail:
    @pytest.mark.parametrize(
        "email,expected",
        [
            ("test@example.com", True),
            ("user.name@domain.co", True),
            ("invalid-email", False),
            ("@no-local-part.com", False),
            ("user@.com", False)
        ]
    )
    def test_validate_email(self, email, expected):
        assert validate_email(email) == expected

    def test_validate_email_type_error(self):
        with pytest.raises(TypeError):
            validate_email(None)


class TestValidateISBN:
    @pytest.mark.parametrize(
        "isbn,expected",
        [
            ("1234567890", True),
            ("1234567890123", True),
            ("12345", False),
            ("abc1234567", False),
            ("", False)
        ]
    )
    def test_validate_isbn(self, isbn, expected):
        assert validate_isbn(isbn) == expected

    def test_validate_isbn_non_string(self):
        with pytest.raises(AttributeError):
            validate_isbn(1234567890)


class TestValidateUserID:
    @pytest.mark.parametrize(
        "user_id,expected",
        [
            (1, True),
            (100, True),
            (0, False),
            (-5, False),
            ("abc", False)
        ]
    )
    def test_validate_user_id(self, user_id, expected):
        assert validate_user_id(user_id) == expected

    def test_validate_user_id_none(self):
        assert validate_user_id(None) is False