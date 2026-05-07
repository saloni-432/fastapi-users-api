import pytest
from sqlalchemy.exc import IntegrityError
from app.crud.user_crud import create_user, get_users, get_user, update_user, delete_user
from app.schemas.user_schemas import UserCreate, UserUpdate

class TestCreateUser:
    def test_creates_user(self, db):
        user = create_user(db, UserCreate(name="Bob", email="bob@test.com"))
        assert user.id is not None
        assert user.name == "Bob"
        assert user.email == "bob@test.com"

    def test_duplicate_email_raises(self, db):
        create_user(db, UserCreate(name="Bob", email="bob@test.com"))
        with pytest.raises(IntegrityError):
            create_user(db, UserCreate(name="Bob2", email="bob@test.com"))

class TestGetUsers:
    def test_empty_list(self, db):
        assert get_users(db) == []

    def test_returns_all_users(self, db):
        create_user(db, UserCreate(name="A", email="a@test.com"))
        create_user(db, UserCreate(name="B", email="b@test.com"))
        assert len(get_users(db)) == 2

class TestGetUser:
    def test_returns_user(self, db, existing_user):
        found = get_user(db, existing_user.id)
        assert found.email == existing_user.email

    def test_returns_none_for_missing(self, db):
        assert get_user(db, 999999) is None

class TestUpdateUser:
    def test_updates_fields(self, db, existing_user):
        updated = update_user(db, existing_user.id, UserUpdate(name="New", email="new@test.com"))
        assert updated.name == "New"
        assert updated.email == "new@test.com"

    def test_returns_error_for_missing(self, db):
        result = update_user(db, 999999, UserUpdate(name="X", email="x@test.com"))
        assert result == {"error": "User not found"}

class TestDeleteUser:
    def test_deletes_user(self, db, existing_user):
        result = delete_user(db, existing_user.id)
        assert result == {"message": "User deleted successfully"}
        assert get_user(db, existing_user.id) is None

    def test_returns_error_for_missing(self, db):
        result = delete_user(db, 999999)
        assert result == {"error": "User not found"}
