from datetime import datetime, timedelta, timezone
from functools import cache
from typing import Optional

from aiomysql import Pool
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from starlette import status

from app.models.pydantic import Semester, User
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


async def get_current_user(
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
    user = await user_service.get_user(username, db)
    if user is None:
        raise credentials_exception

    return User(**user.dict())  # turn UserInDB into User instance


def get_semester(
    year: Optional[int] = None, semester: Optional[int] = None
) -> Semester:
    if year is not None and semester is None:
        raise ValueError("A semester must be passed if a year is passed.")
    if semester is not None and year is None:
        raise ValueError("A year must be passed if a semester is passed.")

    if year is None and semester is None:
        return _current_semester()

    return Semester(year=year, semester=semester)


def _current_semester() -> Semester:
    """Get the current semester."""

    # Get the current time, taking into account that a semester starts and ends at noon
    # rather than midnight (UTC).
    t = datetime.now(tz=timezone.utc) - timedelta(hours=12)
    now_year = t.year
    now_month = t.month

    if now_month < 5:
        return Semester(year=now_year - 1, semester=2)
    elif now_month < 11:
        return Semester(year=now_year, semester=1)
    else:
        return Semester(year=now_year, semester=2)
