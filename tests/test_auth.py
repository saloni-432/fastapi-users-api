from jose import JWTError, jwt
import pytest
from app.auth import (
    verify_password,
    create_access_token,
    get_password_hash,
    SECRET_KEY,
    ALGORITHM,
)

class TestPasswordHashing:
    def test_hash_not_plaintext(self):
        h = get_password_hash("mypass")
        assert h != "mypass"

    def test_verify_correct(self):
        h = get_password_hash("mypass")
        assert verify_password("mypass", h) is True

    def test_verify_wrong(self):
        h = get_password_hash("mypass")
        assert verify_password("wrong", h) is False

    def test_verify_empty(self):
        h = get_password_hash("mypass")
        assert verify_password("", h) is False

class TestJWTTokens:
    def test_token_is_string(self):
        token = create_access_token({
            "username": "alice",
            "role": "user",
        })

        assert isinstance(token, str)

    def test_token_contains_subject(self):
        token = create_access_token({
            "username": "alice",
            "role": "user",
        })

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload["sub"] == "alice"
        assert payload["role"] == "user"
        assert payload["type"] == "access"

    def test_token_contains_expiry(self):
        token = create_access_token({
            "username": "alice",
            "role": "user",
        })

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert "exp" in payload

    def test_wrong_secret_raises(self):
        token = create_access_token({
            "username": "alice",
            "role": "user",
        })

        with pytest.raises(JWTError):
            jwt.decode(token, "WRONG_SECRET", algorithms=[ALGORITHM])
