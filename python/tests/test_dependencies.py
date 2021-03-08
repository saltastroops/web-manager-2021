from typing import Any, Dict, Optional

import pytest
from _pytest.monkeypatch import MonkeyPatch
from aiomysql import Pool
from fastapi import HTTPException
from jose import jwt

from app.dependencies import get_current_user, get_settings
from app.models.pydantic import UserInDB
from app.service import user as user_service
from app.settings import Settings


def test_get_settings(monkeypatch: MonkeyPatch) -> None:
    """get_settings reads in environment variables."""
    monkeypatch.setenv("SECRET_KEY", "very-secret")

    settings = get_settings()

    assert settings.secret_key == "very-secret"


@pytest.mark.parametrize(
    "token_payload",
    [
        # no token payload
        {},
        # wrong token payloads
        {"su": "johndoe"},
        {"sur": "johndoe"},
        {"subs": "johndoe"},
        # non-existing username
        {"sub": "john"},
    ],
)
def test_get_current_user_fails_for_invalid_token(
    token_payload: Dict[str, Any], monkeypatch: MonkeyPatch
) -> None:
    """get_current_user fails for invalid tokens."""

    def mock_get_user(username: str) -> Optional[UserInDB]:
        if username == "johndoe":
            return UserInDB(username="johndoe", hashed_password="whatever")
        return None

    monkeypatch.setattr(user_service, "get_user", mock_get_user)

    # create the token
    secret_key = "very-secret"
    token = jwt.encode(token_payload, secret_key, algorithm="HS256")

    with pytest.raises(HTTPException) as excinfo:
        get_current_user(Settings(secret_key=secret_key), token)
    assert excinfo.value.status_code == 401


def test_get_current_user_fails_for_corrupted_token() -> None:
    secret_key = "very-secret"
    token = "corrupted-token"
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(Settings(secret_key=secret_key), token)
    assert excinfo.value.status_code == 401


def test_get_current_user_returns_user(monkeypatch: MonkeyPatch) -> None:
    def mock_get_user(username: str) -> Optional[UserInDB]:
        if username == "johndoe":
            return UserInDB(username="johndoe", hashed_password="whatever")
        return None

    monkeypatch.setattr(user_service, "get_user", mock_get_user)

    # create the token
    secret_key = "very-secret"
    token = jwt.encode({"sub": "johndoe"}, secret_key, algorithm="HS256")

    user = get_current_user(Settings(secret_key=secret_key), token)
    assert user.username == "johndoe"
    assert not hasattr(user, "hashed_password")
