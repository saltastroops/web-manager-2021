import base64
import re
from typing import Optional
from urllib.parse import unquote

import pytest
from _pytest.monkeypatch import MonkeyPatch
from aiomysql import Pool
from requests import Session
from starlette import status

from app.main import app
from app.models.general import User
from app.service import user as user_service
from app.util import auth


def user(username: str) -> User:
    return User(
        email="sipho@example.com",
        family_name="Nkosi",
        given_name="Sipho",
        username=username,
    )


def test_get_login_form_without_redirect(client: Session) -> None:
    response = client.get("/login")

    assert response.status_code == 200

    assert "login" in response.text.lower()
    assert "username or password" not in response.text.lower()  # no error message

    assert 'action="/login?redirect=Lw==' in response.text


def test_get_login_form_with_redirect(client: Session) -> None:
    redirect = "L3Byb3Bvc2Fscwo="
    response = client.get(f"/login?redirect={redirect}")

    assert response.status_code == 200

    assert "login" in response.text.lower()
    assert "username or password" not in response.text.lower()  # no error message

    assert f'action="/login?redirect={redirect}"' in response.text


@pytest.mark.parametrize(
    "username,password",
    [("", ""), ("", "whatever"), ("vuyo", ""), ("mary", "incorrect")],
)
def test_login_incorrect_credentials_are_rejected(
    username: str, password: str, client: Session, monkeypatch: MonkeyPatch
) -> None:
    """The login page rejects incorrect user credentials."""

    async def mock_authenticate_user(
        username: str, password: str, db: Pool
    ) -> Optional[User]:
        if password != "secret":
            return None
        return user(username=username)

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

    async def mock_authenticate_user(
        username: str, password: str, db: Pool
    ) -> Optional[User]:
        if password != "secret":
            return None
        return user(username=username)

    monkeypatch.setattr(auth, "authenticate_user", mock_authenticate_user)

    response = client.post("/login", data={"username": "khaya", "password": "secret"})

    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert "Location" in response.headers
    assert response.headers["Location"] == "/"


def test_login_redirect_after_logging_in(
    client: Session, monkeypatch: MonkeyPatch
) -> None:
    """The login page redirects after logging in."""

    async def mock_authenticate_user(
        username: str, password: str, db: Pool
    ) -> Optional[User]:
        if password != "secret":
            return None
        return user(username=username)

    redirect = base64.b64encode(b"/proposals").decode("utf-8")

    monkeypatch.setattr(auth, "authenticate_user", mock_authenticate_user)

    response = client.post(
        f"/login?redirect={redirect}", data={"username": "khaya", "password": "secret"}
    )

    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert "Location" in response.headers
    assert response.headers["Location"] == "/proposals"


def test_login_sets_authorization_cookie(
    client: Session, monkeypatch: MonkeyPatch
) -> None:
    """An Authorization cookie is set when logging in is successful."""

    async def mock_authenticate_user(
        username: str, password: str, db: Pool
    ) -> Optional[User]:
        if password != "secret":
            return None
        return user(username=username)

    monkeypatch.setattr(auth, "authenticate_user", mock_authenticate_user)

    response = client.post("/login", data={"username": "khaya", "password": "secret"})

    quoted_cookie_value = response.cookies["Authorization"]
    cookie_value = unquote(quoted_cookie_value)
    assert cookie_value.startswith("Bearer ")


def test_redirect_to_login_for_missing_auth(client: Session) -> None:
    """Secured pages redirect unauthenticated users to the login page."""
    response = client.get("/proposals")

    # the test client follows the redirect to the login page
    assert response.status_code == 200
    assert "login" in response.text.lower()
    match = re.search(r'redirect=([^"]*)"', response.text)
    assert match
    redirect = base64.b64decode(match.group(1)).decode("utf-8")
    assert "/proposals" in redirect


def test_redirect_after_successful_login(
    client: Session, monkeypatch: MonkeyPatch
) -> None:
    """The user is redirected to the originally requested page if they had to login."""

    async def mock_authenticate_user(
        username: str, password: str, db: Pool
    ) -> Optional[User]:
        if password != "secret":
            return None
        return user(username=username)

    async def mock_get_user(username: str, db: Pool) -> User:
        return user(username="siya")

    monkeypatch.setattr(auth, "authenticate_user", mock_authenticate_user)
    monkeypatch.setattr(user_service, "get_user", mock_get_user)

    # try to access a secured page
    response = client.get("/proposals")

    # extract the URL to which the login credentials should be submitted
    match = re.search(r'action\s*=\s*"([^"]*)"', response.text)
    assert match
    url = match.group(1)
    response = client.post(url, data={"username": "siya", "password": "secret"})

    # go to that URL (which should be for the secured page)
    redirect_url = response.headers.get("Location")
    assert redirect_url
    response = client.get(redirect_url)
    assert "proposals" in response.text.lower()

    # clean up
    app.dependency_overrides = {}
