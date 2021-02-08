from typing import Generator

import pytest
from requests import Session
from starlette.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client() -> Generator[Session, None, None]:
    with TestClient(app) as client:
        yield client
