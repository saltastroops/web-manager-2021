"""Tests for block related API routes."""
from requests import Session
from starlette import status


def test_get_block_html_requires_auth(client: Session) -> None:
    """The user must be authenticated to request block html."""
    response = client.get("/api/proposals/2020-2-SCI-042/blocks/abcd9876.html")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
