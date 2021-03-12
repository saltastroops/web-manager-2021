"""Unit tests for the database pool."""
import os

import pytest
from aiomysql import Pool

from app.util.database import DatabasePool
from tests.markers import nodatabase


@pytest.mark.asyncio
@nodatabase
async def test_database_pool_can_be_connected_called_and_closed():
    """A DatabasePool instance can be created, connected, called and closed."""
    dsn = os.getenv("SDB_DSN")
    if not dsn:
        raise ValueError(
            "The SDB_DSN environment variable is not set or its value is "
            "an empty string. Set the variable value to a database DSN, "
            "or mark the test with markers.nodatabase to skip it. Tests "
            "with this marker are still executed if the SDB_DSN variable "
            "is set and does not contain an empty string."
        )

    database_pool = DatabasePool()
    await database_pool.connect(dsn)

    try:
        assert isinstance(database_pool(), Pool)
    finally:
        await database_pool.close()


def test_database_pool_connect_must_called_first():
    """
    For a DatabasePool instance the connect method must be called before the instance
    can be called.
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

    database_pool = DatabasePool()
    with pytest.raises(ValueError) as excinfo:
        database_pool()
    assert "connect" in str(excinfo)
