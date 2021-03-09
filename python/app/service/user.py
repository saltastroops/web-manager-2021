"""User service."""
from aiomysql import Pool

from app.models.pydantic import User, UserInDB


async def get_user(username: str, db: Pool) -> UserInDB:
    sql = """
SELECT
    Username,
    Password,
    FirstName,
    Surname,
    Email
FROM PiptUser AS u
    JOIN Investigator AS i ON (u.Investigator_Id=i.Investigator_Id)
WHERE Username=%(username)s
"""
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, {"username": username})
            r = await cur.fetchone()
            if r is None:
                raise ValueError(f"There exists no user for the username {username}.")

    return UserInDB(
        email=r.email,
        family_name=r.family_name,
        given_name=r.given_name,
        hashed_password=r.hashed_password,
        username=r.username,
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
