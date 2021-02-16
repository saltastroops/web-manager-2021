import base64
from typing import Optional
from urllib.parse import unquote

import pytest
from _pytest.monkeypatch import MonkeyPatch
from requests import Session
from starlette import status

from app.models.pydantic import User
from app.settings import Settings
from app.util import auth


def test_get_login_form_without_redirect(client: Session) -> None:
    response = client.get("/login")

    assert response.status_code == 200

    assert "login" in response.text.lower()
    assert "username or password" not in response.text.lower()  # no error message

    print(response.text)
    assert 'action="/login?redirect=Lw==' in response.text


def test_get_login_form_with_redirect(client: Session) -> None:
    redirect = "L3Byb3Bvc2Fscwo="
    response = client.get(f"/login?redirect={redirect}")

    assert response.status_code == 200

    assert "login" in response.text.lower()
    assert "username or password" not in response.text.lower()  # no error message

    assert f'action="/login?redirect={redirect}"' in response.text


@pytest.mark.parametrize(
    "username,password", [("", ""), ("", "whatever"), ("vuyo", ""), ("mary", "incorrect")]
)
def test_login_incorrect_credentials_are_rejected(
        username: str, password: str, client: Session, monkeypatch: MonkeyPatch
) -> None:
    """The login page rejects incorrect user credentials."""

    def mock_authenticate_user(username: str, password: str) -> Optional[User]:
        if password != "secret":
            return None
        return User(username=username)

    monkeypatch.setattr(auth, "authenticate_user", mock_authenticate_user)

    response = client.post("/login", data={"username": username, "password": password})

    assert response.status_code == 200

    assert "login" in response.text.lower()
    assert "username or password" in response.text.lower()
    assert username in response.text
    if password != "":
        assert password not in response.text


def test_login_home_after_logging_in(client: Session, monkeypatch: MonkeyPatch) -> None:
    """The login page by default redirects to the home page after logging in."""

    def mock_authenticate_user(username: str, password: str) -> Optional[User]:
        if password != "secret":
            return None
        return User(username=username)

    monkeypatch.setattr(auth, "authenticate_user", mock_authenticate_user)

    response = client.post("/login", data={"username": "khaya", "password": "secret"})

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert "Location" in response.headers
    assert response.headers["Location"] == "/"


def test_login_redirect_after_logging_in(client: Session, monkeypatch: MonkeyPatch) -> None:
    """The login page redirects after logging in."""

    def mock_authenticate_user(username: str, password: str) -> Optional[User]:
        if password != "secret":
            return None
        return User(username=username)

    redirect = base64.b64encode(b"/proposals").decode("utf-8")

    monkeypatch.setattr(auth, "authenticate_user", mock_authenticate_user)

    response = client.post(f"/login?redirect={redirect}", data={"username": "khaya", "password": "secret"})

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert "Location" in response.headers
    assert response.headers["Location"] == "/proposals"


def test_login_sets_authorization_cookie(client: Session, monkeypatch: MonkeyPatch) -> None:
    """An Authorization is set when logging in is successful."""

    def mock_authenticate_user(username: str, password: str) -> Optional[User]:
        if password != "secret":
            return None
        return User(username=username)

    monkeypatch.setattr(auth, "authenticate_user", mock_authenticate_user)

    response = client.post("/login", data={"username": "khaya", "password": "secret"})

    quoted_cookie_value = response.cookies["Authorization"]
    cookie_value = unquote(quoted_cookie_value)
    assert cookie_value.startswith("Bearer ")


def test_redirect_to_login_for_missing_auth(client: Session):
    response = client.get("/proposals")
    print(response.text)
    redirect = base64.b64encode(b"/proposals").decode("utf-8")

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert "Location" in response.headers
    assert response.headers["Location"] == f"/login?redirect={redirect}"
