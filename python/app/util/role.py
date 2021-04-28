from abc import ABC

from aiomysql import Pool

from app.models.general import User
from app.service import user as user_service


class Role(ABC):
    """
    A user role.
    """

    async def is_assigned_to(self, user: User) -> bool:
        """
        Check whether a user has this role.
        """
        raise NotImplementedError()  # pragma: no cover


class Administrator(Role):
    """
    The role of being an administrator.
    """

    def __init__(self, db: Pool):
        self.db = db

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_administrator(user, self.db)


class Investigator(Role):
    """
    The role of being an investigator on a proposal.
    """

    def __init__(self, proposal_code: str, db: Pool):
        self.proposal_code = proposal_code
        self.db = db

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_investigator(user, self.proposal_code, self.db)


class MaskCutter(Role):
    """
    The role of being an administrator.
    """

    def __init__(self, db: Pool):
        self.db = db

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_mask_cutter(user, self.db)


class PartnerTacChair(Role):
    """
    The role of being a chair of the Time Allocation Committee of a partner.
    """

    def __init__(self, partner_code: str, db: Pool):
        self.partner_code = partner_code
        self.db = db

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_partner_tac_chair(user, self.partner_code, self.db)


class PartnerTacMember(Role):
    """
    The role of being a member of the Time Allocation Committee of a partner.
    """

    def __init__(self, partner_code: str, db: Pool):
        self.partner_code = partner_code
        self.db = db

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_partner_tac_member(
            user, self.partner_code, self.db
        )


class PrincipalContact(Role):
    """
    The role of being the Principal Contact for a proposal.
    """

    def __init__(self, proposal_code: str, db: Pool):
        self.proposal_code = proposal_code
        self.db = db

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_principal_contact(
            user, self.proposal_code, self.db
        )


class PrincipalInvestigator(Role):
    """
    The role of being the Principal Investigator for a proposal.
    """

    def __init__(self, proposal_code: str, db: Pool):
        self.proposal_code = proposal_code
        self.db = db

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_principal_investigator(
            user, self.proposal_code, self.db
        )


class ProposalTacChair(Role):
    """
    The role of being a chair of the Time Allocation Committee for a proposal.
    """

    def __init__(self, proposal_code: str, db: Pool):
        self.proposal_code = proposal_code
        self.db = db

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_proposal_tac_chair(
            user, self.proposal_code, self.db
        )


class ProposalTacMember(Role):
    """
    The role of being a member of the Time Allocation Committee for a proposal.
    """

    def __init__(self, proposal_code: str, db: Pool):
        self.proposal_code = proposal_code
        self.db = db

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_proposal_tac_member(
            user, self.proposal_code, self.db
        )


class SaltAstronomer(Role):
    """
    The role of being a SALT Astronomer.
    """

    def __init__(self, db: Pool):
        self.db = db

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_salt_astronomer(user, self.db)


class SaltEngineer(Role):
    """
    The role of being in the SALT Technical Operations team.
    """

    def __init__(self, db: Pool):
        self.db = db

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_salt_engineer(user, self.db)


class SaltOperator(Role):
    """
    The role of being a SALT operator.
    """

    def __init__(self, db: Pool):
        self.db = db

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_salt_operator(user, self.db)
