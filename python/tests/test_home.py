"""Unit tests for the home page"""
from starlette.testclient import TestClient


def test_home_is_rendered(client: TestClient):
    """The home page is rendered."""
    response = client.get("/")

    assert response.status_code == 200
    assert "SALT" in response.text
    assert "Web Manager" in response.text
