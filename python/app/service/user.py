"""User service."""
from aiomysql import Pool

from app.models.general import User, UserInDB


async def get_user(username: str, db: Pool) -> UserInDB:
    sql = """
SELECT
    Email,
    Surname,
    FirstName,
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
    """
    Check whether a user is an administrator.

    If the user does not exist, it is assumed they are no administrator.
    """
    sql = """
SELECT COUNT(*)
FROM PiptUserSetting pus
JOIN PiptSetting ps ON pus.PiptSetting_Id = ps.PiptSetting_Id
JOIN PiptUser pu ON pus.PiptUser_Id = pu.PiptUser_Id
WHERE pu.Username = %(username)s
      AND ps.PiptSetting_Name='RightAdmin'
      AND pus.Value >= 2;
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, {"username": user.username})
            (count,) = await cur.fetchone()
            return int(count) > 0


async def is_investigator(user: User, proposal_code: str, db: Pool) -> bool:
    """
    Check whether a user is an investigator on a proposal.

    If the user does not exist, it is assumed they are no investigator.
    """
    sql = """
SELECT COUNT(*)
FROM ProposalCode pc
JOIN ProposalInvestigator pi ON pc.ProposalCode_Id = pi.ProposalCode_Id
JOIN Investigator I on pi.Investigator_Id = I.Investigator_Id
JOIN PiptUser pu ON I.Investigator_Id = pu.Investigator_Id
WHERE pc.Proposal_Code=%(proposal_code)s AND pu.Username=%(username)s
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                sql, {"proposal_code": proposal_code, "username": user.username}
            )
            (count,) = await cur.fetchone()
            return int(count) > 0


async def is_mask_cutter(user: User, db: Pool) -> bool:
    """
    Check whether a user cuts slit masks.

    If the user does not exist, it is assumed they don't cut masks.
    """
    return user.username == "cutter42"


async def is_partner_tac_chair(user: User, partner_code: str, db: Pool) -> bool:
    """
    Check whether a user is a TAC chair for a partner.

    If the user does not exist, it is assumed they are no TAC chair.
    """
    sql = """
SELECT COUNT(*)
FROM PiptUserTAC putac
JOIN PiptUser pu ON putac.PiptUser_Id = pu.PiptUser_Id
JOIN Partner p ON putac.Partner_Id = p.Partner_Id
WHERE pu.Username=%(username)s AND p.Partner_Code=%(partner_code)s AND putac.Chair=1;
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                sql, {"username": user.username, "partner_code": partner_code}
            )
            (count,) = await cur.fetchone()
            return True if count > 0 else False


async def is_partner_tac_member(user: User, partner_code: str, db: Pool) -> bool:
    """
    Check whether a user is a TAC member for a partner.

    TAC chairs are TAC members as well.

    If the user does not exist, it is assumed they
    are no TAC member.
    """
    sql = """
SELECT COUNT(*)
FROM PiptUserTAC putac
JOIN PiptUser pu ON putac.PiptUser_Id = pu.PiptUser_Id
JOIN Partner p ON putac.Partner_Id = p.Partner_Id
WHERE pu.Username=%(username)s AND p.Partner_Code=%(partner_code)s
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                sql, {"username": user.username, "partner_code": partner_code}
            )
            (count,) = await cur.fetchone()
            return True if count > 0 else False


async def is_principal_contact(user: User, proposal_code: str, db: Pool) -> bool:
    """
    Check whether a user is the Principal Contact of a proposal.

    If the user does not exist, it is assumed they are no Principal Contact.
    """

    sql = """
    SELECT COUNT(*)
    FROM ProposalCode pcode
    JOIN ProposalContact pcontact ON pcode.ProposalCode_Id = pcontact.ProposalCode_Id
    JOIN Investigator i ON pcontact.Contact_Id=i.Investigator_Id
    JOIN PiptUser pu ON i.PiptUser_Id=pu.PiptUser_Id
    WHERE pcode.Proposal_Code=%(proposal_code)s AND pu.Username=%(username)s
        """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                sql, {"proposal_code": proposal_code, "username": user.username}
            )
            (count,) = await cur.fetchone()
            return True if count > 0 else False


async def is_principal_investigator(user: User, proposal_code: str, db: Pool) -> bool:
    """
    Check whether a user is the Principal Investigator of a proposal.

    If the user does not exist, it is assumed they are no Principal Investigator.
    """
    sql = """
SELECT COUNT(*)
FROM ProposalCode pcode
JOIN ProposalContact pcontact ON pcode.ProposalCode_Id = pcontact.ProposalCode_Id
JOIN Investigator i ON pcontact.Leader_Id=i.Investigator_Id
JOIN PiptUser pu ON i.PiptUser_Id=pu.PiptUser_Id
WHERE pcode.Proposal_Code=%(proposal_code)s AND pu.Username=%(username)s
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                sql, {"proposal_code": proposal_code, "username": user.username}
            )
            (count,) = await cur.fetchone()
            return True if count > 0 else False


async def is_proposal_tac_chair(user: User, proposal_code: str, db: Pool) -> bool:
    """
    Check whether a user is TAC chair of a TAC from which a proposal has requested time.

    If an investigator on a proposal belongs to a partner, but no time is requested for
    that partner, a TAC chair for that partner is _not_ considered a TAC chair for the
    proposal.

    If the user does not exist, it is assumed they are no TAC chair.
    """
    sql = """
SELECT COUNT(*)
FROM ProposalCode pc
JOIN MultiPartner mp on pc.ProposalCode_Id = mp.ProposalCode_Id
JOIN Partner p ON mp.Partner_Id = p.Partner_Id
JOIN PiptUserTAC put on p.Partner_Id = put.Partner_Id
JOIN PiptUser pu ON put.PiptUser_Id = pu.PiptUser_Id
WHERE pc.Proposal_Code=%(proposal_code)s
      AND pu.Username=%(username)s
      AND mp.ReqTimePercent>0
      AND put.Chair=1;
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                sql, {"proposal_code": proposal_code, "username": user.username}
            )
            (count,) = await cur.fetchone()
            return True if count > 0 else False


async def is_proposal_tac_member(user: User, proposal_code: str, db: Pool) -> bool:
    """
    Check whether a user is TAC member of a TAC from which a proposal has requested
    time.

    If an investigator on a proposal belongs to a partner, but no time is requested for
    that partner, a TAC member for that partner is _not_ considered a TAC member for the
    proposal.

    If the user does not exist, it is assumed they are no TAC member.
    """
    sql = """
SELECT COUNT(*)
FROM ProposalCode pc
JOIN MultiPartner mp on pc.ProposalCode_Id = mp.ProposalCode_Id
JOIN Partner p ON mp.Partner_Id = p.Partner_Id
JOIN PiptUserTAC put on p.Partner_Id = put.Partner_Id
JOIN PiptUser pu ON put.PiptUser_Id = pu.PiptUser_Id
WHERE pc.Proposal_Code=%(proposal_code)s
      AND pu.Username=%(username)s
      AND mp.ReqTimePercent>0;
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                sql, {"proposal_code": proposal_code, "username": user.username}
            )
            (count,) = await cur.fetchone()
            return True if count > 0 else False


async def is_salt_astronomer(user: User, db: Pool) -> bool:
    """
    Check whether a user is a SALT Astronomer.

    If the user does not exist, it is assumed they are no SALT Astronomer.
    """
    sql = """
SELECT COUNT(*)
FROM PiptUser pu
JOIN PiptUserSetting pus ON pu.PiptUser_Id = pus.PiptUser_Id
JOIN PiptSetting ps ON pus.PiptSetting_Id = ps.PiptSetting_Id
WHERE ps.PiptSetting_Name='RightAstronomer' AND pu.Username=%(username)s
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, {"username": user.username})
            (count,) = await cur.fetchone()
            return True if count > 0 else False


async def is_salt_engineer(user: User, db: Pool) -> bool:
    """
    Check whether a user is a SALT engineer.

    If the user does not exist, it is assumed they are no SALT engineer.
    """
    return False


async def is_salt_operator(user: User, db: Pool) -> bool:
    """
    Check whether a user is a SALT Operator.

    If the user does not exist, it is assumed they are no SALT Operator.
    """
    sql = """
SELECT COUNT(*)
FROM PiptUser pu
JOIN PiptUserSetting pus ON pu.PiptUser_Id = pus.PiptUser_Id
JOIN PiptSetting ps ON pus.PiptSetting_Id = ps.PiptSetting_Id
WHERE ps.PiptSetting_Name='RightOperator' AND pu.Username=%(username)s
    """
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, {"username": user.username})
            (count,) = await cur.fetchone()
            return True if count > 0 else False
