import os

import dotenv

# Make sure that the test database etc. are used.
# IMPORTANT: These lines must be executed before any server-related package is imported.

os.environ["DOTENV_FILE"] = ".env.test"
dotenv.load_dotenv(os.environ["DOTENV_FILE"])

from typing import Generator, cast  # noqa: E402

import aiomysql  # noqa: E402
import dsnparse  # noqa: E402
import pytest  # noqa: E402
from aiomysql import Pool  # noqa: E402
from requests import Session  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402

from app.dependencies import get_db, get_settings  # noqa: E402
from app.main import app  # noqa: E402
from app.settings import Settings  # noqa: E402


def mock_get_settings() -> Settings:
    return Settings(secret_key="top-secret")


class MockDatabasePool:
    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def __call__(self) -> Pool:
        return cast(Pool, {})


@pytest.fixture()
async def db() -> Pool:
    """
    Database fixture.

    The fixture value is an aiomysql database pool for the database specified in the
    SDB_DSN environment variable.
    """
    dsn = os.getenv("SDB_DSN")
    if not dsn:
        raise ValueError(
            "The SDB_DSN environment variable is not set or its value is "
            "an empty string. Set the variable value to a database DSN, "
            "or mark the test with markers.nodatabase to skip it. Tests "
            "with this marker are still executed if the SDB_DSN variable "
            "is set and does not contain an empty string."
        )

    r = dsnparse.parse(dsn)
    pool = await aiomysql.create_pool(
        host=r.host,
        port=r.port,
        user=r.username,
        password=r.password,
        db=r.database,
    )

    yield pool

    pool.close()
    await pool.wait_closed()


@pytest.fixture()
def client() -> Generator[Session, None, None]:
    """A client which does not authenticate the user."""
    app.dependency_overrides[get_settings] = mock_get_settings
    app.dependency_overrides[get_db] = MockDatabasePool()

    with TestClient(app) as client:
        yield client

        app.dependency_overrides = {}


@pytest.fixture(scope="module")
def settings() -> Generator[Settings, None, None]:
    yield mock_get_settings()
