import asyncio
from asyncio import Task
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:  # avoid circular import issues
    from app.util.permission import Permission  # pragma: no cover
    from app.util.role import Role  # pragma: no cover

from pydantic import BaseModel


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    email: str
    family_name: str
    given_name: str
    username: str

    async def has_role_of(self, role: "Role") -> bool:
        """
        Check whether the user has a role.

        If you need to check whether the user has at least one of a list of roles, you
        should use the method has_any_role_of instead of calling has_role_of multiple
        times.

        This method uses the role's is_assigned_to method for performing the check.
        """
        return await role.is_assigned_to(self)

    async def has_any_role_of(self, *roles: "Role") -> bool:
        """
        Check whether the user has any of a list of roles.

        False is returned if the list of roles is empty.

        If you need to check whether the user has at least one of a list of roles, you
        should use this method rather than calling the has_role_of method for each of
        the roles.
        """

        if len(roles) == 0:
            return False

        # asyncio.wait must be used with tasks
        tasks = [asyncio.create_task(self.has_role_of(role)) for role in roles]

        # loop until the user has a role or all roles have been checked
        while True:
            done, pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_COMPLETED
            )

            # check whether the user has any of the roles whose checks have completed
            for done_task in done:
                if done_task.result() is True:
                    # the user has a role, so there is no need to continue checking
                    for pending_task in pending:
                        pending_task.cancel()
                    return True

                # the completed tasks are removed, as otherwise we would loop needlessly
                # over the while loop while while waiting for the next task to complete
                tasks.remove(cast(Task[bool], done_task))

            # all checks have completed, and the user has none of the roles
            if not pending:
                return False

    async def is_permitted_to(self, permission: "Permission") -> bool:
        """
        Check whether this user has a permission.

        This method uses the permission's is_permitted_for method for performing the
        check.
        """
        return await permission.is_permitted_for(self)


class UserInDB(User):
    hashed_password: str
