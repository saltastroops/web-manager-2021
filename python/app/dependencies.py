from functools import cache

from aiomysql import Pool
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from starlette import status

from app.models.pydantic import User
from app.service import user as user_service
from app.settings import Settings
from app.util.auth import ALGORITHM, OAuth2TokenOrCookiePasswordBearer
from app.util.database import DatabasePool


@cache  # for performance reasons, as the function is called for every request
def get_settings() -> Settings:
    """Get the Web Manager settings."""
    return Settings()


get_db = DatabasePool()


oauth2_scheme = OAuth2TokenOrCookiePasswordBearer("api/token")


def get_current_user(
    settings: Settings = Depends(get_settings),
    token: str = Depends(oauth2_scheme),
    db: Pool = Depends(get_db),
) -> User:
    """Get the currently logged in user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = user_service.get_user(username)
    if user is None:
        raise credentials_exception

    return User(**user.dict())  # turn UserInDB into User instance
