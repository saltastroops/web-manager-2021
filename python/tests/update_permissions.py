from aiomysql import connect

ADMINISTRATOR = 3
TAC_CHAIR = 4
TAC_MEMBER = 5
DOUBLE_TAC_MEMBER = 18
ASTRONOMER = 6
ENGINEER = 7
OPERATOR = 8
PI = 19
PC = 20
INVESTIGATOR = 1


async def set_admin_permissions(admin_id: int, test_db_connection: connect) -> None:
    update_admin_permissions_sql = f"""
INSERT INTO PiptUserSetting
    (PiptUser_Id, PiptSetting_Id, Value)
VALUES
    (%s, %s, %s)
ON DUPLICATE KEY UPDATE
    PiptUser_Id=%s, PiptSetting_Id=%s, Value=%s;
"""
    cursor = await test_db_connection.cursor()
    await cursor.execute(update_admin_permissions_sql, (admin_id, 22, 3, admin_id, 22, 3))


async def set_sa_permissions(sa_id: int, test_db_connection: connect) -> None:
    update_sa_permissions_sql = f"""
INSERT INTO PiptUserSetting
    (PiptUser_Id, PiptSetting_Id, Value)
VALUES
    (%s, %s, %s)
ON DUPLICATE KEY UPDATE
    PiptUser_Id=%s, PiptSetting_Id=%s, Value=%s;
"""
    cursor = await test_db_connection.cursor()
    await cursor.execute(update_sa_permissions_sql, (sa_id, 21, 3, sa_id, 21, 3))


async def set_so_permissions(so_id: int, test_db_connection: connect) -> None:
    update_so_permissions_sql = f"""
INSERT INTO PiptUserSetting
    (PiptUser_Id, PiptSetting_Id, Value)
VALUES
    (%s, %s, %s)
ON DUPLICATE KEY UPDATE
    PiptUser_Id=%s, PiptSetting_Id=%s, Value=%s;
"""
    cursor = await test_db_connection.cursor()
    await cursor.execute(update_so_permissions_sql, (so_id, 23, 3, so_id, 23, 3))


async def give_users_right_proposal_permissions(test_db_connection: connect, pi_id: int, pc_id: int,
                                                investigator_id: int) -> None:
    update_users_right_proposal_permissions_sql = f"""
INSERT INTO PiptUserSetting
    (PiptUser_Id, PiptSetting_Id, Value)
VALUES
    (%s, %s, %s)
ON DUPLICATE KEY UPDATE
    PiptUser_Id=%s, PiptSetting_Id=%s, Value=%s;
"""
    data = [
        (pi_id, 20, 3, pi_id, 20, 3),
        (pc_id, 20, 3, pc_id, 20, 3),
        (investigator_id, 20, 3, investigator_id, 20, 3)
    ]
    cursor = await test_db_connection.cursor()
    await cursor.executemany(update_users_right_proposal_permissions_sql, data)


async def set_known_users_own_proposal(test_db_connection: connect, pi_id, pc_id, sa_id: int, investigator_id) -> None:
    # Proposal to be own is 2020-1-SCI-001 with id 2623
    proposal_code_id = 2623
    update_proposal_owners_sql = f"""
UPDATE ProposalContact
SET Leader_Id=%s, Contact_Id=%s, Astronomer_Id=%s
WHERE ProposalCode_Id=%s;
"""
    cursor = await test_db_connection.cursor()
    await cursor.execute(update_proposal_owners_sql, (pi_id, pc_id,sa_id, proposal_code_id))

    data = [
        (proposal_code_id, pi_id, 1),
        (proposal_code_id, pc_id, 1),
        (proposal_code_id, investigator_id, 1),
    ]
    insert_proposal_investigator_sql = f"""
INSERT INTO ProposalContact
    (ProposalCode_Id, Investigator_Id, InvestigatorOkay)
VALUES
    (%s, %s, %s)
ON DUPLICATE KEY UPDATE
    ProposalCode_Id=%s, Investigator_Id=%s, InvestigatorOkay=%s;
"""
    cursor = await test_db_connection.cursor()
    await cursor.executemany(insert_proposal_investigator_sql, data)

#Todo search how to set the user to be a engineer


async def set_tac_permissions(tac_id: int, tac_chair_id: int, double_tac_id: int, test_db_connection: connect) -> None:

    data = [
        (tac_id, 3, 0, tac_id, 3, 0),
        (tac_chair_id, 3, 1, tac_chair_id, 3, 1),
        (double_tac_id, 3, 0, double_tac_id, 3, 0),
        (double_tac_id, 1, 0, double_tac_id, 1, 0),
    ]
    update_tac_permissions_sql = f"""
INSERT INTO PiptUserTac
    (PiptUser_Id, Partner_Id, Chain)
VALUES
    (%s, %s, %s)
ON DUPLICATE KEY UPDATE
    PiptUser_Id=%s, PiptSetting_Id=%s, Value=%s;
"""
    cursor = await test_db_connection.cursor()
    await cursor.execute(update_tac_permissions_sql, data)


async def create_known_users(test_db_connection: connect) -> None:
    # Create a username.
    # Admin user id is 3

    data =[
        ("Admin", ADMINISTRATOR),
        ("TacChain", TAC_CHAIR),
        ("TacMember", TAC_MEMBER),
        ("DoubleTacMember", DOUBLE_TAC_MEMBER),
        ("Astronomer", ASTRONOMER),
        ("Engineer", ENGINEER),
        ("Operator", OPERATOR),
        ("Pi", PI),
        ("Pc", PC),
        ("Investigator", INVESTIGATOR)
    ]
    update_username_sql = f"""
UPDATE PiptUser
SET Username = %s
WHERE PiptUser_Id = %s;
"""
    cursor = await test_db_connection.cursor()
    await cursor.executemany(update_username_sql, data)
    await set_admin_permissions(ADMINISTRATOR, test_db_connection)
    await set_sa_permissions(ASTRONOMER, test_db_connection)
    await set_so_permissions(OPERATOR, test_db_connection)
    await set_pi_permissions(test_db_connection)
    await set_pc_permissions(PC, test_db_connection)
    await set_investigator_permissions(INVESTIGATOR, test_db_connection)
    await set_known_users_own_proposal(
        test_db_connection=test_db_connection, pi_id=PI, pc_id=PC, sa_id=ASTRONOMER, investigator_id=INVESTIGATOR)
    await set_tac_permissions(
        tac_id=TAC_MEMBER, tac_chair_id=TAC_CHAIR, double_tac_id=DOUBLE_TAC_MEMBER,
        test_db_connection=test_db_connection)
