"""Unit tests for the proposal page."""
from requests import Session


def test_proposal_requires_auth(client: Session) -> None:
    """The user must be authenticated to view the proposal page."""
    response = client.get("/proposals/2020-2-SCI-017")

    assert "Login" in response.text
