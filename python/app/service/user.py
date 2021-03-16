"""User service."""
from aiomysql import Pool

from app.models.pydantic import User, UserInDB


async def get_user(username: str, db: Pool) -> UserInDB:
    sql = """
SELECT
    Email,
    FirstName,
    Surname,
    Password,
    Username
FROM PiptUser AS pu
    JOIN Investigator AS i ON (pu.Investigator_Id=i.Investigator_Id)
WHERE Username=%(username)s
"""
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, {"username": username})
            r = await cur.fetchone()
            if r is None:
                raise ValueError(f"There exists no user for the username {username}.")

    return UserInDB(
        email=r[0],
        family_name=r[1],
        given_name=r[2],
        hashed_password=r[3],
        username=r[4],
    )


async def is_administrator(user: User, db: Pool) -> bool:
    """Check whether a user is an administrator."""
    sql = """
SELECT COUNT(*) AS c
FROM PiptUserSetting pus
JOIN PiptSetting ps ON pus.PiptSetting_Id = ps.PiptSetting_Id
JOIN PiptUser pu ON pus.PiptUser_Id = pu.PiptUser_Id
WHERE pu.Username = %(username)s
      AND ps.PiptSetting_Name='RightAdmin'
      AND pus.Value >= 2;
    """
    with db.acquire() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"username": user.username})
            (r,) = cur.fetchone()
            return int(r) > 0


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
