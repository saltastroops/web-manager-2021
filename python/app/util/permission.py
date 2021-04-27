from abc import ABC

from aiomysql import Pool

from app.models.general import User
from app.util import role


class Permission(ABC):
    """
    A user permission.

    All permissions should be implemented in terms of roles. In other words, checking
    whether a user has a permission should always mean checking whether a user has some
    role.
    """

    async def is_permitted_for(self, user: User) -> bool:
        """
        Check whether a user has this permission.
        """
        raise NotImplementedError()  # pragma: no cover


class ViewProposal(Permission):
    """
    Permission to view a proposal.

    A user may view a proposal if at least one of the following is true.

    - The user is an investigator on the proposal.
    - The user is a SALT Astronomer.
    - The user is a SALT Operator.
    - The user is a SALT Engineer.
    - The user is a TAC member for a partner from which the proposal has requested time.
    - The user is an administrator.
    """

    def __init__(self, proposal_code: str, db: Pool):
        self.proposal_code = proposal_code
        self.db = db

    async def is_permitted_for(self, user: User) -> bool:
        """Check whether a user has the permission."""

        roles = [
            role.Investigator(self.proposal_code, self.db),
            role.SaltAstronomer(self.db),
            role.SaltOperator(self.db),
            role.SaltEngineer(self.db),
            role.ProposalTacMember(self.proposal_code, self.db),
            role.Administrator(self.db),
        ]

        return await user.has_any_role_of(*roles)
