import os
from typing import Generator, cast

import dotenv
import pytest
from _pytest.monkeypatch import MonkeyPatch
from aiomysql import Pool
from requests import Session
from starlette.testclient import TestClient

from app.dependencies import get_db, get_settings
from app.main import app
from app.settings import Settings


def mock_get_settings() -> Settings:
    return Settings(secret_key="top-secret")


class MockDatabasePool:
    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def __call__(self) -> Pool:
        return cast(Pool, {})


@pytest.fixture(autouse=True)
def ignore_dotenv_file(monkeypatch: MonkeyPatch) -> None:
    """
    Ignore the variables defined in the .env file.

    The settings for the server are read from a .env file, irrespective of whether the
    server is started by a unit test. To avoid this, this fixture reads the .env file
    and then explicitly sets its environment variables to an empty string, unless the
    respective variable is defined as a system environment variable as well.
    """
    system_variables = set(os.environ.keys())
    dotenv_variables = set(dotenv.dotenv_values().keys())
    for name in dotenv_variables:
        if name not in system_variables:
            monkeypatch.setenv(name, "")


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
