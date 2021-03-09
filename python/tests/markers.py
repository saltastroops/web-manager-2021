"""pytest markers."""
import os

import pytest

"""
Skip a test if no test database is defined.

This marker should be used on all tests that require a database. The marker checks
whether the environment variable TEST_SDB_DSN is defined. This is the variable used by
the db fixture to create a database connection. It can be included in the .env file.
"""
nodatabase = pytest.mark.skipif(
    os.getenv("WEB_MANAGER_TEST_DATABASE_DSN") is None,
    reason="No test database defined. See the tests.markers package for details.",
)
