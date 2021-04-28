"""Unit tests for permissions."""
import pytest
from aiomysql import Pool

from app.models.general import User
from app.util import permission
from tests.markers import nodatabase


def user(username: str) -> User:
    return User(
        email="user@example.com",
        family_name="User",
        given_name="Salt",
        username=username,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "username,proposal_code,expected_is_permitted",
    (
        # TODO: Add test for SALT Engineer.
        ("non-existing", "2020-2-SCI-043", False),
        ("tanyalewis", "non-existing", False),
        ("tanyalewis", "2020-1-SCI-007", False),  # wrong proposal
        ("tanyalewis", "2020-2-SCI-043", True),  # investigator
        ("bryanmark", "2020-2-SCI-043", True),  # SALT Astronomer
        ("william63", "2020-2-SCI-043", True),  # SALT Operator
        ("andersonkevin", "2020-2-SCI-043", True),  # TAC chair
        ("hkim", "2020-2-SCI-043", True),  # TAC member
        ("felicia47", "2020-2-SCI-043", False),  # wrong TAC
        ("lindsey12", "2020-2-SCI-043", True),  # administrator
        ("angelaherrera", "2020-2-SCI-043", True)
        # SALT Astronomer and administrator
    ),
)
@nodatabase
async def test_view_proposal(
    username: str, proposal_code: str, expected_is_permitted: bool, db: Pool
) -> None:
    view_proposal = permission.ViewProposal(proposal_code, db)

    assert await view_proposal.is_permitted_for(user(username)) == expected_is_permitted
