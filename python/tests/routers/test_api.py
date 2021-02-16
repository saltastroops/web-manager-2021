from typing import Optional

import pytest
from _pytest.monkeypatch import MonkeyPatch
from requests import Session
from starlette import status

from app.models.pydantic import User
from app.settings import Settings
from app.util import auth


@pytest.mark.parametrize(
    "username,password",
    [
        ("", ""),
        ("", "secret"),
        ("sipho", ""),
        ("pieter", "pieter-pw"),
        ("pieter", "pieter-pwt"),
        ("pieter", "pieter-pwdd"),
    ],
)
def test_token_for_incorrect_credentials(
    username: str, password: str, client: Session, monkeypatch: MonkeyPatch
) -> None:
    """Calling /api/token with incorrect credentials gives a 401 error."""

    def mock_authenticate_user(username: str, password: str) -> Optional[User]:
        if username + "-pwd" == password:
            return User(username=username)
        return None

    monkeypatch.setattr(auth, "authenticate_user", mock_authenticate_user)

    resp = client.post("/api/token", data={"username": username, "password": password})

    assert resp.status_code in [
        status.HTTP_422_UNPROCESSABLE_ENTITY,  # missing username or password
        status.HTTP_401_UNAUTHORIZED,  # wrong username or password
    ]


def test_token_returns_authentication_token(
    client: Session, monkeypatch: MonkeyPatch, settings: Settings
) -> None:
    """/api/token returns a valid authentication token."""

    def mock_authenticate_user(username: str, password: str) -> Optional[User]:
        if username + "-pwd" == password:
            return User(username=username)
        return None

    monkeypatch.setattr(auth, "authenticate_user", mock_authenticate_user)

    # request a token...
    resp = client.post("/api/token", data={"username": "jane", "password": "jane-pwd"})
    token = resp.json()["access_token"]

    # ... and check that it is valid
    user = auth.get_current_user(settings, token)
    assert user.username == "jane"
