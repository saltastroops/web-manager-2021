from abc import ABC

from app.models.pydantic import User
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

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_administrator(user)


class Investigator(Role):
    """
    The role of being an investigator on a proposal.
    """

    def __init__(self, proposal_code: str):
        self.proposal_code = proposal_code

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_investigator(user, self.proposal_code)


class MaskCutter(Role):
    """
    The role of being an administrator.
    """

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_mask_cutter(user)


class PartnerTacChair(Role):
    """
    The role of being a chair of the Time Allocation Committee of a partner.
    """

    def __init__(self, partner_code: str):
        self.partner_code = partner_code

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_partner_tac_chair(user, self.partner_code)


class PartnerTacMember(Role):
    """
    The role of being a member of the Time Allocation Committee of a partner.
    """

    def __init__(self, partner_code: str):
        self.partner_code = partner_code

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_partner_tac_member(user, self.partner_code)


class PrincipalContact(Role):
    """
    The role of being the Principal Contact for a proposal.
    """

    def __init__(self, proposal_code: str):
        self.proposal_code = proposal_code

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_principal_contact(user, self.proposal_code)


class PrincipalInvestigator(Role):
    """
    The role of being the Principal Investigator for a proposal.
    """

    def __init__(self, proposal_code: str):
        self.proposal_code = proposal_code

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_principal_investigator(user, self.proposal_code)


class ProposalTacChair(Role):
    """
    The role of being a chair of the Time Allocation Committee for a proposal.
    """

    def __init__(self, proposal_code: str):
        self.proposal_code = proposal_code

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_proposal_tac_chair(user, self.proposal_code)


class ProposalTacMember(Role):
    """
    The role of being a member of the Time Allocation Committee for a proposal.
    """

    def __init__(self, proposal_code: str):
        self.proposal_code = proposal_code

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_proposal_tac_member(user, self.proposal_code)


class SaltAstronomer(Role):
    """
    The role of being a SALT Astronomer.
    """

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_salt_astronomer(user)


class SaltEngineer(Role):
    """
    The role of being in the SALT Technical Operations team.
    """

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_salt_engineer(user)


class SaltOperator(Role):
    """
    The role of being a SALT operator.
    """

    async def is_assigned_to(self, user: User) -> bool:
        return await user_service.is_salt_operator(user)
