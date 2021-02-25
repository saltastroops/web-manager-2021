import hashlib
import pathlib

import pytest

from app.jinja2.filters import autoversion


@pytest.mark.parametrize(
    "url,filter_value",
    [
        (
            "http://example.com/static/css/main.css",
            "http://example.com/static/css/main.css?v=HASH",
        ),
        (
            "https://example.com/static/css/main.css",
            "https://example.com/static/css/main.css?v=HASH",
        ),
        (
            "https://example.com:80/static/css/main.css",
            "https://example.com:80/static/css/main.css?v=HASH",
        ),
        (
            "https://www.example.com/static/css/main.css#somewhere",
            "https://www.example.com/static/css/main.css?v=HASH#somewhere",
        ),
        (
            "https://www.example.com/static/css/main.css?limit=43",
            "https://www.example.com/static/css/main.css?limit=43&v=HASH",
        ),
        (
            "https://www.example.com/static/css/main.css?limit=43#somewhere",
            "https://www.example.com/static/css/main.css?limit=43&v=HASH#somewhere",
        ),
        ("/static/css/main.css", "/static/css/main.css?v=HASH"),
    ],
)
def test_autoversion(url: str, filter_value: str) -> None:
    """The autoversion filter is working correctly."""

    # Get the MD5 hash of the (real) file static/css/main.css
    h = hashlib.md5()
    with open(pathlib.Path("static") / "css" / "main.css", "rb") as f:
        content = f.read()
    h.update(content)
    hash_value = h.hexdigest()

    # sanity check
    assert hash_value

    # check the filter
    assert autoversion(url) == filter_value.replace("HASH", hash_value)


def test_autoversion_does_not_accept_relative_filepaths() -> None:
    """The autoversion filter does not accept relative file paths."""
    with pytest.raises(ValueError) as excinfo:
        autoversion("static/css/main.css")

    assert "relative" in str(excinfo)


def test_autoversion_does_not_accept_directories() -> None:
    """The autoversion filter does not accept directories."""
    with pytest.raises(ValueError) as excinfo:
        autoversion("/static/css")

    assert "directories" in str(excinfo)


def test_autoversion_missing_file() -> None:
    """The autoversion filter raises a meaningful error if the file does not exist."""
    with pytest.raises(IOError) as excinfo:
        autoversion("/static/css/i_dont_exist.css")

    assert "i_dont_exist.css" in str(excinfo)
