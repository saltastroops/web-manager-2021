"""User service."""
from app.models.pydantic import User, UserInDB
from app.util import auth


def get_user(username: str) -> UserInDB:
    return UserInDB(
        username=username, hashed_password=auth.get_password_hash("!" + username)
    )


async def is_administrator(user: User) -> bool:
    return user.username == "admin42"


async def is_mask_cutter(user: User) -> bool:
    return user.username == "cutter42"


async def is_investigator(user: User, proposal_code: str) -> bool:
    return proposal_code.endswith("042")


async def is_partner_tac_chair(user: User, partner_code: str) -> bool:
    return partner_code == "AMNH"


async def is_partner_tac_member(user: User, partner_code: str) -> bool:
    return partner_code == "AMNH"


async def is_principal_contact(user: User, proposal_code: str) -> bool:
    return proposal_code.endswith("024")


async def is_principal_investigator(user: User, proposal_code: str) -> bool:
    return proposal_code.endswith("022")


async def is_proposal_tac_chair(user: User, proposal_code: str) -> bool:
    return proposal_code.endswith("023")


async def is_proposal_tac_member(user: User, proposal_code: str) -> bool:
    return proposal_code.endswith("023")


async def is_salt_astronomer(user: User) -> bool:
    return user.username == "astronomer"


async def is_salt_engineer(user: User) -> bool:
    return user.username == "engineer"


async def is_salt_operator(user: User) -> bool:
    return user.username == "operator"
