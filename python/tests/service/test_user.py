"""Unit tests for the user service."""

import pytest
from aiomysql import Pool

from app.models.general import User
from app.service import user as user_service
from tests.markers import nodatabase


def user(username: str) -> User:
    return User(
        email="user@example.com",
        family_name="User",
        given_name="Some",
        username=username,
    )


# get_user


@nodatabase
@pytest.mark.asyncio
async def test_get_user_raises_an_exception_for_unknown_user(db: Pool) -> None:
    """get_user raises an error if the username does not exist."""
    with pytest.raises(ValueError):
        await user_service.get_user("x67hndst", db)


@nodatabase
@pytest.mark.asyncio
async def test_get_user_returns_the_correct_user(db: Pool) -> None:
    """get_user returns the correct user details."""
    user = await user_service.get_user("fieldswilliam", db)

    assert user.email == "diana.vincent@email.com"
    assert user.family_name == "Vincent"
    assert user.given_name == "Diana"
    assert user.username == "fieldswilliam"


# is_administrator


@nodatabase
@pytest.mark.asyncio
async def test_is_administrator_returns_false_for_non_existing_user(db: Pool) -> None:
    """is_administrator returns False for a non-existing user."""
    is_admin = await user_service.is_administrator(user("hjfd6843dg"), db)

    assert is_admin is False


@nodatabase
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username,expected_is_admin", [("gcook", False), ("angelaherrera", True)]
)
async def test_is_administrator_returns_correct_value(
    username: str, expected_is_admin: bool, db: Pool
) -> None:
    """is_administrator returns whether a user is administrator."""
    is_admin = await user_service.is_administrator(user(username), db)

    assert is_admin == expected_is_admin


# is_investigator


@nodatabase
@pytest.mark.asyncio
async def test_is_investigator_returns_false_for_non_existing_user(db: Pool) -> None:
    """is_investigator returns False if the user does not exist."""
    is_investigator = await user_service.is_investigator(
        user("hsvcbiigfv"), "2020-2-SCI-043", db
    )

    assert is_investigator is False


@nodatabase
@pytest.mark.asyncio
async def test_is_investigator_returns_false_for_non_existing_proposal_code(
    db: Pool,
) -> None:
    """is_investigator returns False if the proposal code does not exist."""
    is_investigator = await user_service.is_investigator(
        user("hsvcbiigfv"), "unknown_code", db
    )

    assert is_investigator is False


@nodatabase
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username,proposal_code,expected_is_investigator",
    (
        ("tanyalewis", "2020-2-SCI-043", True),
        ("ruthdixon", "2020-2-SCI-043", False),
        ("tanyalewis", "2018-2-LSP-001", False),
        ("ruthdixon", "2018-2-LSP-001", True),
        ("markclark", "2018-2-LSP-001", True),
    ),
)
async def test_is_investigator_returns_correct_value(
    username: str, proposal_code: str, expected_is_investigator: bool, db: Pool
) -> None:
    """is_investigator returns the correct value."""
    is_investigator = await user_service.is_investigator(
        user(username), proposal_code, db
    )

    assert is_investigator == expected_is_investigator


# is_mask_cutter


@nodatabase
@pytest.mark.asyncio
@pytest.mark.skip
async def test_is_mask_cutter_returns_false_for_non_existing_user(
    db: Pool,
) -> None:
    """is_mask_cutter returns False if the user does not exist."""
    is_mask_cutter = await user_service.is_mask_cutter(user("hsvcbiigfv"), db)

    assert is_mask_cutter is False


@nodatabase
@pytest.mark.asyncio
@pytest.mark.parametrize("username,expected_is_mask_cutter", (("abc", True),))
@pytest.mark.skip
async def test_is_mask_cutter_returns_correct_value(
    username: str,
    expected_is_mask_cutter: bool,
    db: Pool,
) -> None:
    """is_mask_cutter returns the correct value."""
    is_mask_cutter = await user_service.is_mask_cutter(user("hsvcbiigfv"), db)

    assert is_mask_cutter is False


# is_partner_tac_chair


@nodatabase
@pytest.mark.asyncio
@pytest.mark.skip
async def test_is_partner_tac_chair_returns_false_for_non_existing_user(
    db: Pool,
) -> None:
    """is_partner_tac_chair returns False if the user does not exist."""
    is_partner_tac_chair = await user_service.is_partner_tac_chair(
        user("hsvcbiigfv"), "RSA", db
    )

    assert is_partner_tac_chair is False


@nodatabase
@pytest.mark.asyncio
async def test_is_partner_tac_chair_returns_false_for_non_existing_partner_code(
    db: Pool,
) -> None:
    """is_partner_tac_chair returns False if the partner code does not exist."""
    is_partner_tac_chair = await user_service.is_partner_tac_chair(
        user("tanyalewis"), "unknown_partner", db
    )

    assert is_partner_tac_chair is False


@nodatabase
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username,partner_code,expected_is_partner_tac_chair",
    (
        ("heathelizabeth", "RSA", False),
        ("andersonkevin", "RSA", True),
        ("hkim", "RSA", False),
        ("felicia47", "AMNH", True),
        ("felicia47", "RSA", False),
    ),
)
async def test_is_partner_tac_chair_returns_correct_value(
    username: str, partner_code: str, expected_is_partner_tac_chair: bool, db: Pool
) -> None:
    """is_partner_tac_chair returns the correct value."""
    is_partner_tac_chair = await user_service.is_partner_tac_chair(
        user(username), partner_code, db
    )

    assert is_partner_tac_chair == expected_is_partner_tac_chair


# is_partner_tac_member


@nodatabase
@pytest.mark.asyncio
@pytest.mark.skip
async def test_is_partner_tac_member_returns_false_for_non_existing_user(
    db: Pool,
) -> None:
    """is_partner_tac_member returns False if the user does not exist."""
    is_partner_tac_member = await user_service.is_partner_tac_member(
        user("hsvcbiigfv"), "RSA", db
    )

    assert is_partner_tac_member is False


@nodatabase
@pytest.mark.asyncio
async def test_is_partner_tac_member_returns_false_for_non_existing_partner_code(
    db: Pool,
) -> None:
    """is_partner_tac_member returns False if the partner code does not exist."""
    is_partner_tac_member = await user_service.is_partner_tac_member(
        user("tanyalewis"), "unknown_partner", db
    )

    assert is_partner_tac_member is False


@nodatabase
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username,partner_code,expected_is_partner_tac_member",
    (
        ("heathelizabeth", "RSA", False),
        ("andersonkevin", "RSA", True),
        ("hkim", "RSA", True),
        ("felicia47", "AMNH", True),
        ("felicia47", "RSA", False),
    ),
)
async def test_is_partner_tac_member_returns_correct_value(
    username: str, partner_code: str, expected_is_partner_tac_member: bool, db: Pool
) -> None:
    """is_partner_tac_member returns the correct value."""
    is_partner_tac_member = await user_service.is_partner_tac_member(
        user(username), partner_code, db
    )

    assert is_partner_tac_member == expected_is_partner_tac_member


# is_principal_contact


@nodatabase
@pytest.mark.asyncio
async def test_is_principal_contact_returns_false_for_non_existing_user(
    db: Pool,
) -> None:
    """is_principal_contact returns False if the user does not exist."""
    is_principal_contact = await user_service.is_principal_contact(
        user("hsvcbiigfv"), "2020-2-SCI-043", db
    )

    assert is_principal_contact is False


@nodatabase
@pytest.mark.asyncio
async def test_is_principal_contact_returns_false_for_non_existing_proposal_code(
    db: Pool,
) -> None:
    """is_principal_contact returns False if the proposal code does not exist."""
    is_principal_contact = await user_service.is_principal_contact(
        user("tanyalewis"), "non-existing", db
    )

    assert is_principal_contact is False


@nodatabase
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username,proposal_code,expected_is_principal_contact",
    (
        ("ruthdixon", "2018-2-LSP-001", False),
        ("joefields", "2018-2-LSP-001", True),
        ("tanyalewis", "2018-2-LSP-001", False),
        ("tanyalewis", "2020-2-SCI-043", True),
        ("ruthdixon", "2020-2-SCI-043", False),
    ),
)
async def test_is_principal_contact_returns_correct_value(
    username: str, proposal_code: str, expected_is_principal_contact: bool, db: Pool
) -> None:
    """is_principal_contact returns the correct value."""
    is_principal_contact = await user_service.is_principal_contact(
        user(username), proposal_code, db
    )

    assert is_principal_contact == expected_is_principal_contact


# is_principal_investigator


@nodatabase
@pytest.mark.asyncio
async def test_is_principal_investigator_returns_false_for_non_existing_user(
    db: Pool,
) -> None:
    """is_principal_investigator returns False if the user does not exist."""
    is_principal_investigator = await user_service.is_principal_investigator(
        user("hsvcbiigfv"), "2020-2-SCI-043", db
    )

    assert is_principal_investigator is False


@nodatabase
@pytest.mark.asyncio
async def test_is_principal_investigator_returns_false_for_non_existing_proposal_code(
    db: Pool,
) -> None:
    """is_principal_investigator returns False if the proposal code does not exist."""
    is_principal_investigator = await user_service.is_principal_investigator(
        user("tanyalewis"), "non-existing", db
    )

    assert is_principal_investigator is False


@nodatabase
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username,proposal_code,expected_is_principal_investigator",
    (
        ("ruthdixon", "2018-2-LSP-001", True),
        ("joefields", "2018-2-LSP-001", False),
        ("tanyalewis", "2018-2-LSP-001", False),
        ("tanyalewis", "2020-2-SCI-043", True),
        ("ruthdixon", "2020-2-SCI-043", False),
    ),
)
async def test_is_principal_investigator_returns_correct_value(
    username: str,
    proposal_code: str,
    expected_is_principal_investigator: bool,
    db: Pool,
) -> None:
    """is_principal_investigator returns the correct value."""
    is_principal_investigator = await user_service.is_principal_investigator(
        user(username), proposal_code, db
    )

    assert is_principal_investigator == expected_is_principal_investigator


# is_proposal_tac_chair


@nodatabase
@pytest.mark.asyncio
async def test_is_proposal_tac_chair_returns_false_for_non_existing_user(
    db: Pool,
) -> None:
    """is_proposal_tac_chair returns False if the user does not exist."""
    is_proposal_tac_chair = await user_service.is_proposal_tac_chair(
        user("hsvcbiigfv"), "RSA", db
    )

    assert is_proposal_tac_chair is False


@nodatabase
@pytest.mark.asyncio
async def test_is_proposal_tac_chair_returns_false_for_non_existing_(
    db: Pool,
) -> None:
    """is_proposal_tac_chair returns False if the proposal code does not exist."""
    is_proposal_tac_chair = await user_service.is_proposal_tac_chair(
        user("tanyalewis"), "non-existing", db
    )

    assert is_proposal_tac_chair is False


@nodatabase
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username,proposal_code,expected_is_proposal_tac_chair",
    (
        ("rossrichard", "2020-2-SCI-005", True),
        ("andersonkevin", "2020-2-SCI-005", False),
        ("tanyalewis", "2020-2-SCI-005", False),
        ("andersonkevin", "2018-2-LSP-001", True),
        ("hkim", "2018-2-LSP-002", False),
    ),
)
async def test_is_proposal_tac_chair_returns_correct_value(
    username: str, proposal_code: str, expected_is_proposal_tac_chair: bool, db: Pool
) -> None:
    """is_proposal_tac_chair returns the correct value."""
    is_proposal_tac_chair = await user_service.is_proposal_tac_chair(
        user(username), proposal_code, db
    )

    assert is_proposal_tac_chair == expected_is_proposal_tac_chair


# is_proposal_tac_member


@nodatabase
@pytest.mark.asyncio
async def test_is_proposal_tac_member_returns_false_for_non_existing_user(
    db: Pool,
) -> None:
    """is_proposal_tac_member returns False if the user does not exist."""
    is_proposal_tac_member = await user_service.is_proposal_tac_member(
        user("hsvcbiigfv"), "RSA", db
    )

    assert is_proposal_tac_member is False


@nodatabase
@pytest.mark.asyncio
async def test_is_proposal_tac_member_returns_false_for_non_existing_(
    db: Pool,
) -> None:
    """is_proposal_tac_member returns False if the proposal code does not exist."""
    is_proposal_tac_member = await user_service.is_proposal_tac_member(
        user("tanyalewis"), "non-existing", db
    )

    assert is_proposal_tac_member is False


@nodatabase
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username,proposal_code,expected_is_proposal_tac_member",
    (
        ("rossrichard", "2020-2-SCI-005", True),
        ("andersonkevin", "2020-2-SCI-005", False),
        ("tanyalewis", "2020-2-SCI-005", False),
        ("andersonkevin", "2018-2-LSP-001", True),
        ("hkim", "2018-2-LSP-001", True),
    ),
)
async def test_is_proposal_tac_member_returns_correct_value(
    username: str, proposal_code: str, expected_is_proposal_tac_member: bool, db: Pool
) -> None:
    """is_proposal_tac_member returns the correct value."""
    is_proposal_tac_member = await user_service.is_proposal_tac_member(
        user(username), proposal_code, db
    )

    assert is_proposal_tac_member == expected_is_proposal_tac_member


# is_salt_astronomer


@nodatabase
@pytest.mark.asyncio
async def test_is_salt_astronomer_returns_false_for_non_existing_user(
    db: Pool,
) -> None:
    """is_salt_astronomer returns False if the user does not exist."""
    is_salt_astronomer = await user_service.is_salt_astronomer(user("hsvcbiigfv"), db)

    assert is_salt_astronomer is False


@nodatabase
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username,expected_is_salt_astronomer",
    (("andersonkevin", False), ("bryanmark", True)),
)
async def test_is_salt_astronomer_returns_correct_value(
    username: str, expected_is_salt_astronomer: bool, db: Pool
) -> None:
    """is_salt_astronomer returns the correct value."""
    is_salt_astronomer = await user_service.is_salt_astronomer(user(username), db)

    assert is_salt_astronomer == expected_is_salt_astronomer


# is_salt_engineer


@nodatabase
@pytest.mark.asyncio
@pytest.mark.skip
async def test_is_salt_engineer_returns_false_for_non_existing_user(
    db: Pool,
) -> None:
    """is_salt_engineer returns False if the user does not exist."""
    is_salt_engineer = await user_service.is_salt_engineer(user("hsvcbiigfv"), db)

    assert is_salt_engineer is False


@nodatabase
@pytest.mark.asyncio
@pytest.mark.skip
@pytest.mark.parametrize(
    "username,expected_is_salt_engineer",
    (("fjvhbdu", True),),
)
async def test_is_salt_engineer_returns_correct_value(
    username: str, expected_is_salt_engineer: bool, db: Pool
) -> None:
    """is_salt_engineer returns the correct value."""
    is_salt_engineer = await user_service.is_salt_engineer(user(username), db)

    assert is_salt_engineer == expected_is_salt_engineer


# is_salt_operator


@nodatabase
@pytest.mark.asyncio
async def test_is_salt_operator_returns_false_for_non_existing_user(
    db: Pool,
) -> None:
    """is_salt_operator returns False if the user does not exist."""
    is_salt_operator = await user_service.is_salt_operator(user("hsvcbiigfv"), db)

    assert is_salt_operator is False


@nodatabase
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username,expected_is_salt_operator",
    (("allenmatthew", False), ("william63", True)),
)
async def test_is_salt_operator_returns_correct_value(
    username: str, expected_is_salt_operator: bool, db: Pool
) -> None:
    """is_salt_operator returns the correct value."""
    is_salt_operator = await user_service.is_salt_operator(user(username), db)

    assert is_salt_operator == expected_is_salt_operator
