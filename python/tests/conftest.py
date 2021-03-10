from typing import Generator, cast

import pytest
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
