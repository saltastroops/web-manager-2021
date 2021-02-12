from _pytest.monkeypatch import MonkeyPatch

from app.dependencies import get_settings


def test_get_settings(monkeypatch: MonkeyPatch) -> None:
    """get_settings reads in environment variables."""
    monkeypatch.setenv("SECRET_KEY", "very-secret")

    settings = get_settings()

    assert settings.secret_key == "very-secret"
