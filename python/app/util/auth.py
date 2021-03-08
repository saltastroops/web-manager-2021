"""
Utility functions for authentication and authorization.

The code in this module has in wide oparts been taken from the FastAPI tutorial,
https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, cast
from urllib.parse import unquote

from aiomysql import Pool
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt
from passlib.context import CryptContext
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from app.models.pydantic import AccessToken, User
from app.service import user as user_service

ALGORITHM = "HS256"

ACCESS_TOKEN_LIFETIME_HOURS = 7 * 24


class OAuth2TokenOrCookiePasswordBearer(OAuth2PasswordBearer):
    """
    Extension of FastAPI's OAuth2PasswordBearer class.

    In addition to being able to supply an authentication token via a bearer token in an
    Authorization HTTP header, the extension allows you to supply the bearer token in a
    cookie named Authorization. This cookie must have been quoted using the %xx escape
    (i.e. the white space between "Bearer" and the actual token value must have been
    replaced with "%20").

    While the extension allows authentication via a cookie, from the point of view of
    the OpenAPI integration by FastAPI, it is completely the same as FastAPI's
    OAuth2PasswordBearer class.

    """

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        if not authorization:
            quoted_token_value = request.cookies.get("Authorization")
            if quoted_token_value:
                authorization = unquote(quoted_token_value)
            else:
                authorization = None
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(password: str, hashed_password: str) -> bool:
    """Check a plain text password against a hash."""
    return cast(bool, pwd_context.verify(password, hashed_password))


def get_password_hash(password: str) -> str:
    """Hash a plain text password."""
    return cast(str, pwd_context.hash(password))


def authenticate_user(username: str, password: str, db: Pool) -> Optional[User]:
    """
    Authenticate a user with a username and password.

    If the combination of username and password are valid, the corresponding user is
    returned. Otherwise None is returned.
    """
    user = user_service.get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return User(**user.dict())  # turn UserInDB into User


def create_jwt_token(
    secret_key: str, payload: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT token."""
    to_encode = payload.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_LIFETIME_HOURS)
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)

    return cast(str, encoded_jwt)


def create_access_token(secret_key: str, user: User) -> AccessToken:
    """Generate an authentication token."""
    token_expires = timedelta(hours=ACCESS_TOKEN_LIFETIME_HOURS)
    token = create_jwt_token(
        secret_key=secret_key,
        payload={"sub": user.username},
        expires_delta=token_expires,
    )

    return AccessToken(access_token=token, token_type="bearer")  # nosec
