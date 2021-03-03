from typing import Generator

import pytest
from requests import Session
from starlette.testclient import TestClient

from app.dependencies import get_settings
from app.main import app
from app.settings import Settings


def mock_get_settings() -> Settings:
    return Settings(secret_key="top-secret")


@pytest.fixture()
def client() -> Generator[Session, None, None]:
    """A client which does not authenticate the user."""
    app.dependency_overrides[get_settings] = mock_get_settings

    with TestClient(app) as client:
        yield client

        app.dependency_overrides = {}


@pytest.fixture(scope="module")
def settings() -> Generator[Settings, None, None]:
    yield mock_get_settings()
