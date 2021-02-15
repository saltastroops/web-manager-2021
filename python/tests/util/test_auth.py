from datetime import timedelta
from time import time
from typing import Any, Dict, Optional, cast

import pytest
from _pytest.monkeypatch import MonkeyPatch
from fastapi import HTTPException
from jose import jwt
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request

from app.models.pydantic import UserInDB
from app.service import user as user_service
from app.util import auth
from app.util.auth import OAuth2TokenOrCookiePasswordBearer


class RequestMock(BaseModel):
    cookies: Dict[str, str]
    headers: Dict[str, str]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "req",  # "request" is a reserved name
    [
        # header and cookie missing
        RequestMock(cookies={}, headers={}),
        # header has correct value, but wrong name
        RequestMock(cookies={}, headers={"Authorizatio": "Bearer abcd"}),
        # header has correct value, but wrong name
        RequestMock(cookies={}, headers={"Authorizations": "Bearer abcd"}),
        # header value has incorrect scheme
        RequestMock(cookies={}, headers={"Authorization": "Beare abcd"}),
        # header value has incorrect scheme
        RequestMock(cookies={}, headers={"Authorization": "Bearers abcd"}),
        # header value has no space between scheme and parameter
        RequestMock(cookies={}, headers={"Authorization": "Bearerabcd"}),
        # cookie has correct value, but wrong name
        RequestMock(cookies={"Authorizatio": "Bearer abcd"}, headers={}),
        # cookie has correct value, but wrong name
        RequestMock(cookies={"Authorizations": "Bearer abcd"}, headers={}),
        # cookie value has incorrect scheme
        RequestMock(cookies={"Authorization": "Beare abcd"}, headers={}),
        # cookie value has incorrect scheme
        RequestMock(cookies={"Authorization": "Bearers abcd"}, headers={}),
        # cookie value has no space between scheme and parameter
        RequestMock(cookies={"Authorization": "Bearerabcd"}, headers={}),
    ],
)
async def test_incorrect_or_missing_headers_and_cookies_are_rejected(
    req: RequestMock,
) -> None:
    """Invalid and missing header/cookie values lead to an authentication error."""

    # Case 1: auto_error is True; an exception is raised
    oauth2_scheme = OAuth2TokenOrCookiePasswordBearer("token")
    with pytest.raises(HTTPException) as excinfo:
        await oauth2_scheme(cast(Request, req))

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED

    # Case 2: auto_error is False; None is returned
    oauth2_scheme = OAuth2TokenOrCookiePasswordBearer("token", auto_error=False)
    assert await oauth2_scheme(cast(Request, req)) is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "req,token",  # "request" is a reserved name
    [
        # there is a token in the headers only
        (RequestMock(cookies={}, headers={"Authorization": "Bearer abcd"}), "abcd"),
        # there is a token both in the headers and the cookies
        (
            RequestMock(
                cookies={"Authorization": "Bearer cookietoken"},
                headers={"Authorization": "Bearer headertoken"},
            ),
            "headertoken",
        ),
        # there is a token in the cookies only
        (RequestMock(cookies={"Authorization": "Bearer efgh"}, headers={}), "efgh"),
    ],
)
async def test_the_header_or_cookie_token_is_returned(
    req: RequestMock, token: str
) -> None:
    """The correct token value is returned."""
    oauth2_scheme = OAuth2TokenOrCookiePasswordBearer("token")
    assert await oauth2_scheme(cast(Request, req)) == token


def test_verify_password() -> None:
    """verify_password verifies a password against a password hash."""
    password = "secret"
    incorrect_password = "secrat"
    hashed_password = auth.get_password_hash(password)

    # correct password
    assert auth.verify_password(password, hashed_password)

    # incorrect password
    assert not auth.verify_password(incorrect_password, hashed_password)


def test_get_password_hash() -> None:
    """test_get_password_hash does not return the original password."""
    password = "secret"
    assert auth.get_password_hash(password) != password


@pytest.mark.parametrize(
    "username,password",
    [
        ("", "secret"),
        ("peter", ""),
        ("peter", "pete"),
        ("peter", "peter!"),
        ("peter", "petes"),
        ("mary", "mary"),  # user does not exist
    ],
)
def test_authenticate_user_with_incorrect_credentials(
    username: str, password: str, monkeypatch: MonkeyPatch
) -> None:
    "authenticate_user returns None for incorrect credentials."

    def mock_get_user(username: str) -> Optional[UserInDB]:
        """Returns a user whose password is equal to the username."""
        if username != "peter":
            return None
        return UserInDB(
            username=username, hashed_password=auth.get_password_hash(username)
        )

    monkeypatch.setattr(user_service, "get_user", mock_get_user)
    assert auth.authenticate_user(username, password) is None


@pytest.mark.parametrize(
    "username,password", [("nosipho", "nosipho"), ("Jane Doe", "Jane Doe")]
)
def test_authenticate_user_with_correct_credentials(
    username: str, password: str, monkeypatch: MonkeyPatch
) -> None:
    """authenticate_user returns a user for correct credentials."""

    def mock_get_user(username: str) -> UserInDB:
        """Returns a user whose password is equal to the username."""
        return UserInDB(
            username=username, hashed_password=auth.get_password_hash(username)
        )

    monkeypatch.setattr(user_service, "get_user", mock_get_user)
    assert auth.authenticate_user(username, password) is not None


@pytest.mark.parametrize("payload", [{"a": "b"}, {"c": 123, "d": True}])
def test_create_jwt_token(payload: Dict[str, Any]) -> None:
    """create_jwt_token creates a JWT token."""
    # create_jwt_token can be called with an expiry time
    secret_key = "top_secret"
    token = auth.create_jwt_token(
        secret_key=secret_key, payload=payload, expires_delta=timedelta(hours=48)
    )
    decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])

    # assert decoded_token == payload would not work, as the decoded token dictionary
    # has an exp key.
    for key in payload:
        assert decoded_token[key] == payload[key]

    # the token expires in 48 hours (= 48 * 3600 seconds)
    assert abs(int(decoded_token["exp"]) - 48 * 3600 - time()) < 5

    # ... or it can be called without an expiry time
    token = auth.create_jwt_token(secret_key=secret_key, payload=payload)
    decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])

    # the token expires in 15 minutes (= 15 * 60 seconds)
    assert abs(int(decoded_token["exp"]) - 15 * 60 - time()) < 5

    # assert decoded_token == payload would not work, as the decoded token dictionary
    # has an exp key.
    for key in payload:
        assert decoded_token[key] == payload[key]


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
        auth.get_current_user(secret_key, token)
    assert excinfo.value.status_code == 401


def test_get_current_user_fails_for_corrupted_token() -> None:
    secret_key = "very-secret"
    token = "corrupted-token"
    with pytest.raises(HTTPException) as excinfo:
        auth.get_current_user(secret_key, token)
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

    user = auth.get_current_user(secret_key, token)
    assert user.username == "johndoe"
    assert not hasattr(user, "hashed_password")
