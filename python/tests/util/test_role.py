from typing import cast

import pytest
from _pytest.monkeypatch import MonkeyPatch
from aiomysql import Pool

from app.models.general import User
from app.service import user as user_service
from app.util import role


def user(username: str) -> User:
    return User(
        email="someone@example.com",
        family_name="One",
        given_name="Some",
        username=username,
    )


def db() -> Pool:
    return cast(Pool, db)


@pytest.mark.asyncio
async def test_administrator_uses_user_service(monkeypatch: MonkeyPatch) -> None:
    """The Administrator role uses the user service."""

    # mock for the required user service function
    async def mock_is_administrator(user: User, db: Pool) -> bool:
        return user.username == "admin"

    monkeypatch.setattr(user_service, "is_administrator", mock_is_administrator)
    mock_non_admin_user = user(username="someone")
    mock_admin_user = user(username="admin")

    administrator = role.Administrator(db=db())
    is_administrator = await administrator.is_assigned_to(mock_non_admin_user)
    assert not is_administrator

    administrator = role.Administrator(db=db())
    is_administrator = await administrator.is_assigned_to(mock_admin_user)
    assert is_administrator


@pytest.mark.asyncio
async def test_investigator_uses_user_service(monkeypatch: MonkeyPatch) -> None:
    """The Investigator role uses the user service."""

    # mock for the required user service function
    async def mock_is_investigator(user: User, proposal_code: str, db: Pool) -> bool:
        return proposal_code.endswith("042")

    monkeypatch.setattr(user_service, "is_investigator", mock_is_investigator)
    mock_user = user(username="someone")

    investigator = role.Investigator(proposal_code="2020-1-SCI-041", db=db())
    is_investigator = await investigator.is_assigned_to(mock_user)
    assert not is_investigator

    investigator = role.Investigator(proposal_code="2020-1-SCI-042", db=db())
    is_investigator = await investigator.is_assigned_to(mock_user)
    assert is_investigator


@pytest.mark.asyncio
async def test_mask_cutter_uses_user_service(monkeypatch: MonkeyPatch) -> None:
    """The MaskCutter role uses the user service."""

    # mock for the required user service function
    async def mock_is_mask_cutter(user: User, db: Pool) -> bool:
        return user.username == "maskcutter"

    monkeypatch.setattr(user_service, "is_mask_cutter", mock_is_mask_cutter)
    mock_non_admin_user = user(username="someone")
    mock_admin_user = user(username="maskcutter")

    mask_cutter = role.MaskCutter(db=db())
    is_mask_cutter = await mask_cutter.is_assigned_to(mock_non_admin_user)
    assert not is_mask_cutter

    mask_cutter = role.MaskCutter(db=db())
    is_mask_cutter = await mask_cutter.is_assigned_to(mock_admin_user)
    assert is_mask_cutter


@pytest.mark.asyncio
async def test_partner_tac_chair_uses_user_service(monkeypatch: MonkeyPatch) -> None:
    """The PartnerTacChair role uses the user service."""

    # mock for the required user service function
    async def mock_is_partner_tac_chair(
        user: User, partner_code: str, db: Pool
    ) -> bool:
        return partner_code == "UW"

    monkeypatch.setattr(user_service, "is_partner_tac_chair", mock_is_partner_tac_chair)
    mock_user = user(username="someone")

    partner_tac_chair = role.PartnerTacChair(partner_code="RSA", db=db())
    is_partner_tac_chair = await partner_tac_chair.is_assigned_to(mock_user)
    assert not is_partner_tac_chair

    partner_tac_chair = role.PartnerTacChair(partner_code="UW", db=db())
    is_partner_tac_chair = await partner_tac_chair.is_assigned_to(mock_user)
    assert is_partner_tac_chair


@pytest.mark.asyncio
async def test_partner_tac_member_uses_user_service(monkeypatch: MonkeyPatch) -> None:
    """The PartnerTacMember role uses the user service."""

    # mock for the required user service function
    async def mock_is_partner_tac_member(
        user: User, partner_code: str, db: Pool
    ) -> bool:
        return partner_code == "IUCAA"

    monkeypatch.setattr(
        user_service, "is_partner_tac_member", mock_is_partner_tac_member
    )
    mock_user = user(username="someone")

    partner_tac_member = role.PartnerTacMember(partner_code="RSA", db=db())
    is_partner_tac_member = await partner_tac_member.is_assigned_to(mock_user)
    assert not is_partner_tac_member

    partner_tac_member = role.PartnerTacMember(partner_code="IUCAA", db=db())
    is_partner_tac_member = await partner_tac_member.is_assigned_to(mock_user)
    assert is_partner_tac_member


@pytest.mark.asyncio
async def test_principal_contact_uses_user_service(monkeypatch: MonkeyPatch) -> None:
    """The PrincipalContact role uses the user service."""

    # mock for the required user service function
    async def mock_is_principal_contact(
        user: User, proposal_code: str, db: Pool
    ) -> bool:
        return proposal_code.endswith("010")

    monkeypatch.setattr(user_service, "is_principal_contact", mock_is_principal_contact)
    mock_user = user(username="someone")

    principal_contact = role.PrincipalContact(proposal_code="2020-2-MLT-009", db=db())
    is_principal_contact = await principal_contact.is_assigned_to(mock_user)
    assert not is_principal_contact

    principal_contact = role.PrincipalContact(proposal_code="2020-2-MLT-010", db=db())
    is_principal_contact = await principal_contact.is_assigned_to(mock_user)
    assert is_principal_contact


@pytest.mark.asyncio
async def test_principal_investigator_uses_user_service(
    monkeypatch: MonkeyPatch,
) -> None:
    """The PrincipalInvestigator role uses the user service."""

    # mock for the required user service function
    async def mock_is_principal_investigator(
        user: User, proposal_code: str, db: Pool
    ) -> bool:
        return proposal_code.endswith("037")

    monkeypatch.setattr(
        user_service, "is_principal_investigator", mock_is_principal_investigator
    )
    mock_user = user(username="someone")

    principal_investigator = role.PrincipalInvestigator(
        proposal_code="2020-2-MLT-040", db=db()
    )
    is_principal_investigator = await principal_investigator.is_assigned_to(mock_user)
    assert not is_principal_investigator

    principal_investigator = role.PrincipalInvestigator(
        proposal_code="2020-2-MLT-037", db=db()
    )
    is_principal_investigator = await principal_investigator.is_assigned_to(mock_user)
    assert is_principal_investigator


@pytest.mark.asyncio
async def test_proposal_tac_chair_uses_user_service(monkeypatch: MonkeyPatch) -> None:
    """The ProposalTacChair role uses the user service."""

    # mock for the required user service function
    async def mock_is_proposal_tac_chair(
        user: User, proposal_code: str, db: Pool
    ) -> bool:
        return proposal_code.endswith("005")

    monkeypatch.setattr(
        user_service, "is_proposal_tac_chair", mock_is_proposal_tac_chair
    )
    mock_user = user(username="someone")

    proposal_tac_chair = role.ProposalTacChair(proposal_code="2020-2-SCI-032", db=db())
    is_proposal_tac_chair = await proposal_tac_chair.is_assigned_to(mock_user)
    assert not is_proposal_tac_chair

    proposal_tac_chair = role.ProposalTacChair(proposal_code="2020-2-SCI-005", db=db())
    is_proposal_tac_chair = await proposal_tac_chair.is_assigned_to(mock_user)
    assert is_proposal_tac_chair


@pytest.mark.asyncio
async def test_proposal_tac_member_uses_user_service(monkeypatch: MonkeyPatch) -> None:
    """The ProposalTacMember role uses the user service."""

    # mock for the required user service function
    async def mock_is_proposal_tac_member(
        user: User, proposal_code: str, db: Pool
    ) -> bool:
        return proposal_code.endswith("027")

    monkeypatch.setattr(
        user_service, "is_proposal_tac_member", mock_is_proposal_tac_member
    )
    mock_user = user(username="someone")

    proposal_tac_member = role.ProposalTacMember(
        proposal_code="2020-2-SCI-019", db=db()
    )
    is_proposal_tac_member = await proposal_tac_member.is_assigned_to(mock_user)
    assert not is_proposal_tac_member

    proposal_tac_member = role.ProposalTacMember(
        proposal_code="2020-2-SCI-027", db=db()
    )
    is_proposal_tac_member = await proposal_tac_member.is_assigned_to(mock_user)
    assert is_proposal_tac_member


@pytest.mark.asyncio
async def test_salt_astronomer_uses_user_service(monkeypatch: MonkeyPatch) -> None:
    """The SaltAstronomer role uses the user service."""

    # mock for the required user service function
    async def mock_is_salt_astronomer(user: User, db: Pool) -> bool:
        return user.username == "astronomer"

    monkeypatch.setattr(user_service, "is_salt_astronomer", mock_is_salt_astronomer)
    mock_non_salt_astronomer = user(username="someone")
    mock_salt_astronomer = user(username="astronomer")

    salt_astronomer = role.SaltAstronomer(db=db())
    is_salt_astronomer = await salt_astronomer.is_assigned_to(mock_non_salt_astronomer)
    assert not is_salt_astronomer

    salt_astronomer = role.SaltAstronomer(db=db())
    is_salt_astronomer = await salt_astronomer.is_assigned_to(mock_salt_astronomer)
    assert is_salt_astronomer


@pytest.mark.asyncio
async def test_salt_engineer_uses_user_service(monkeypatch: MonkeyPatch) -> None:
    """The SaltEngineer role uses the user service."""

    # mock for the required user service function
    async def mock_is_salt_engineer(user: User, db: Pool) -> bool:
        return user.username == "engineer"

    monkeypatch.setattr(user_service, "is_salt_engineer", mock_is_salt_engineer)
    mock_non_salt_engineer = user(username="someone")
    mock_salt_engineer = user(username="engineer")

    salt_engineer = role.SaltEngineer(db=db())
    is_salt_engineer = await salt_engineer.is_assigned_to(mock_non_salt_engineer)
    assert not is_salt_engineer

    salt_engineer = role.SaltEngineer(db=db())
    is_salt_engineer = await salt_engineer.is_assigned_to(mock_salt_engineer)
    assert is_salt_engineer


@pytest.mark.asyncio
async def test_salt_operator_uses_user_service(monkeypatch: MonkeyPatch) -> None:
    """The SaltOperator role uses the user service."""

    # mock for the required user service function
    async def mock_is_salt_operator(user: User, db: Pool) -> bool:
        return user.username == "operator"

    monkeypatch.setattr(user_service, "is_salt_operator", mock_is_salt_operator)
    mock_non_salt_operator = user(username="someone")
    mock_salt_operator = user(username="operator")

    salt_operator = role.SaltOperator(db=db())
    is_salt_operator = await salt_operator.is_assigned_to(mock_non_salt_operator)
    assert not is_salt_operator

    salt_operator = role.SaltOperator(db=db())
    is_salt_operator = await salt_operator.is_assigned_to(mock_salt_operator)
    assert is_salt_operator
