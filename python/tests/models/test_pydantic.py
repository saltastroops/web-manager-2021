"""Unit tests for the pydantic models."""
from typing import List

import pytest

from app.models.pydantic import User
from app.util.permission import Permission
from app.util.role import Role


class FakeRole(Role):
    def __init__(self, has_role: bool):
        self.has_role = has_role

    async def is_assigned_to(self, user: User) -> bool:
        return self.has_role


class FakePermission(Permission):
    def __init__(self, is_permitted: bool):
        self.is_permitted = is_permitted

    async def is_permitted_for(self, user: User) -> bool:
        return self.is_permitted


@pytest.mark.asyncio
async def test_user_has_role_of_returns_correct_value() -> None:
    """The User method has_role_of returns the correct value."""
    user = User(
        email="someone@example.com",
        family_name="Person",
        given_name="Some",
        username="someone",
    )

    assert await user.has_role_of(FakeRole(True)) is True
    assert await user.has_role_of(FakeRole(False)) is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "has_role_values,expected_has_any_role",
    (
        ([], False),
        ([False], False),
        ([False, False], False),
        ([False, False, False, False], False),
        ([True], True),
        ([True, True], True),
        ([True, True, True, True], True),
        ([True, False], True),
        ([False, True], True),
        ([False, False, False, True], True),
        ([False, True, True, False], True),
    ),
)
async def test_user_has_any_role_of(
    has_role_values: List[bool], expected_has_any_role: bool
) -> None:
    """The User method has_any_role_of returns the correct value."""
    roles: List[Role] = [FakeRole(has_role) for has_role in has_role_values]
    user = User(
        email="someone@example.com",
        family_name="Person",
        given_name="Some",
        username="someone",
    )

    assert await user.has_any_role_of(*roles) == expected_has_any_role


@pytest.mark.asyncio
async def test_user_is_permitted_to() -> None:
    """The User method is_permitted_to returns the correct value."""
    user = User(
        email="someone@example.com",
        family_name="Person",
        given_name="Some",
        username="someone",
    )

    assert await user.is_permitted_to(FakePermission(True)) is True
    assert await user.is_permitted_to(FakePermission(False)) is False
