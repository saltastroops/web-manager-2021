"""User service."""
from app.models.pydantic import UserInDB
from app.util import auth


def get_user(username: str) -> UserInDB:
    return UserInDB(
        username=username, hashed_password=auth.get_password_hash("!" + username)
    )
