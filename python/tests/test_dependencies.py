from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import pytest
from _pytest.monkeypatch import MonkeyPatch
from aiomysql import Pool
from fastapi import HTTPException
from freezegun.api import FrozenDateTimeFactory
from jose import jwt

from app.dependencies import get_current_user, get_semester, get_settings
from app.models.pydantic import Semester, UserInDB
from app.service import user as user_service
from app.settings import Settings


def user_in_db(username: str, hashed_password: str) -> UserInDB:
    return UserInDB(
        email="john@example.com",
        family_name="Doe",
        given_name="John",
        hashed_password=hashed_password,
        username=username,
    )


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
@pytest.mark.asyncio
async def test_get_current_user_fails_for_invalid_token(
    token_payload: Dict[str, Any], monkeypatch: MonkeyPatch
) -> None:
    """get_current_user fails for invalid tokens."""

    async def mock_get_user(username: str, db: Pool) -> Optional[UserInDB]:
        if username == "johndoe":
            return user_in_db(username="johndoe", hashed_password="whatever")
        return None

    monkeypatch.setattr(user_service, "get_user", mock_get_user)

    # create the token
    secret_key = "very-secret"
    token = jwt.encode(token_payload, secret_key, algorithm="HS256")

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(Settings(secret_key=secret_key), token)
    assert excinfo.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_fails_for_corrupted_token() -> None:
    secret_key = "very-secret"
    token = "corrupted-token"
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(Settings(secret_key=secret_key), token)
    assert excinfo.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_fails_for_expired_token() -> None:
    # create the token
    secret_key = "very-secret"
    to_encode = {"sub": "johndoe", "exp": datetime.utcnow() - timedelta(seconds=100)}
    token = jwt.encode(to_encode, secret_key, algorithm="HS256")

    secret_key = "very-secret"
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(Settings(secret_key=secret_key), token)
    assert excinfo.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_returns_user(monkeypatch: MonkeyPatch) -> None:
    async def mock_get_user(username: str, db: Pool) -> Optional[UserInDB]:
        if username == "johndoe":
            return user_in_db(username="johndoe", hashed_password="whatever")
        return None

    monkeypatch.setattr(user_service, "get_user", mock_get_user)

    # create the token
    secret_key = "very-secret"
    token = jwt.encode({"sub": "johndoe"}, secret_key, algorithm="HS256")

    # check the token
    user = await get_current_user(Settings(secret_key=secret_key), token)
    assert user.username == "johndoe"
    assert not hasattr(user, "hashed_password")


def test_get_semester_returns_input() -> None:
    """get_semester returns the semester for the year and semester input."""
    assert get_semester(year=2019, semester=1) == Semester(year=2019, semester=1)
    assert get_semester(year=2020, semester=2) == Semester(year=2020, semester=2)


def test_get_semester_year_requires_semester() -> None:
    """If a year is passed to get_semester, a semester must be passed as well."""
    with pytest.raises(ValueError):
        get_semester(year=2020)


def test_get_semester_semester_requires_year() -> None:
    """If a semester is passed to get_semester, a year must be passed as well."""
    with pytest.raises(ValueError):
        get_semester(semester=2)


@pytest.mark.parametrize(
    "now,expected_semester",
    [
        (
            datetime(2021, 5, 1, 11, 59, 59, 0, tzinfo=timezone.utc),
            Semester(year=2020, semester=2),
        ),
        (
            datetime(2021, 5, 1, 12, 0, 0, 1, tzinfo=timezone.utc),
            Semester(year=2021, semester=1),
        ),
        (
            datetime(2021, 11, 1, 11, 59, 59, 0, tzinfo=timezone.utc),
            Semester(year=2021, semester=1),
        ),
        (
            datetime(2021, 11, 1, 12, 0, 0, 1, tzinfo=timezone.utc),
            Semester(year=2021, semester=2),
        ),
    ],
)
def test_get_semester_returns_correct_default_value(
    now: datetime, expected_semester: Semester, freezer: FrozenDateTimeFactory
) -> None:
    """get_semester returns the current semester as default value."""
    freezer.move_to(now)
    assert get_semester() == expected_semester
