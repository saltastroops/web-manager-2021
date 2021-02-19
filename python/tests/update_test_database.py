import os
from random import randint
from typing import List

import click
from aiomysql import connect
from faker import Faker


fake = Faker()
Faker.seed(4321)


async def get_all_investigator_ids(test_db_connection: connect) -> List[int]:
    """
    Get all the investigators ids.
    Parameters
    ----------
    test_db_connection:
        The database connection that have table Investigator as the table.

    Returns
    -------
        A List of investigators ids.

    """
    with test_db_connection.cursor() as cur:
        cur.execute("SELECT Investigator_Id FROM Investigator")
        results = await cur.fetchall()
        return [investigator[0] for investigator in results]


async def get_all_pipt_user_ids(test_db_connection: connect) -> List[int]:
    """
    Get all the pipt users ids.
    Parameters
    ----------
    test_db_connection:
        The database connection that have table PiptUser as the table.

    Returns
    -------
        A List of PIPT user ids.

    """
    with test_db_connection.cursor() as cur:
        cur.execute("SELECT PiptUser_Id FROM PiptUser")
        results = await cur.fetchall()
        return [pipt_user[0] for pipt_user in results]


async def get_all_target_coordinates_id(test_db_connection: connect) -> List[int]:
    """
    Get all the target coordinates ids.
    Parameters
    ----------
    test_db_connection:
        The database connection that have table TargetCoordinates as the table.

    Returns
    -------
        A List of target coordinates ids.

    """
    target_coordinates_ids = []
    with test_db_connection.cursor() as cur:
        cur.execute("SELECT TargetCoordinates_Id FROM TargetCoordinates")
        results = await cur.fetchall()
        return [target_coordinate[0] for target_coordinate in results]


async def update_investigators(test_db_connection: connect, db_cursor: connect().cursor) -> None:
    """
    Generate a query that will update all the sensitive information from the Investigator table.

    Parameters
    ----------
    test_db_connection
        The test database connection
    db_cursor
        The Test database cursor

    Returns
    -------
        None
    """
    investigator_ids = await get_all_investigator_ids(test_db_connection)
    for investigator_id in investigator_ids:
        sql = f"""Update Investigator
SET  FirstName = {fake.first_name()}, Surname = {fake.last_name()}, Email = {fake.email()}, Phone = {fake.phone_number()}
WHERE Investigator_Id = {investigator_id};
    """
        db_cursor.execute(sql)
        test_db_connection.commit()


async def update_pipt_users_query(test_db_connection: connect, db_cursor: connect().cursor) -> None:
    """
    Generate a query that will update all the sensitive information from the PIPT user table.

    Parameters
    ----------
    test_db_connection
        The test database connection
    db_cursor
        The Test database cursor

    Returns
    -------
        None
    """
    pipt_user_ids = await get_all_pipt_user_ids(test_db_connection)
    for pipt_user_id in pipt_user_ids:
        sql = f"""UPDATE PiptUser
SET Username = user-{fake.user_name()}, Password = MD5(user-{pipt_user_id}-{os.getenv("TEST_DB_USER_PASSPHRASE")})
WHERE PiptUser_Id = {pipt_user_id};
    """
        db_cursor.execute(sql)
        test_db_connection.commit()


async def update_target_coordinates_query(test_db_connection: connect, db_cursor: connect().cursor) -> None:
    """
    Generate a query that will update all the sensitive information from the target coordinates table.

    Parameters
    ----------
    test_db_connection
        The test database connection
    db_cursor
        The Test database cursor

    Returns
    -------
        None
    """
    target_coordinates_ids = await get_all_target_coordinates_id(test_db_connection)
    for target_coordinates_id in target_coordinates_ids:
        dec_h = randint(-75, 10)
        sign = "-" if dec_h < 0 else "+"
        sql = f"""UPDATE TargetCoordinates
SET RaH={randint(0, 23)},RaM={randint(0, 59)},RaS={randint(0, 59)},DecSign={sign},DecD={abs(dec_h)},
DecM={randint(0, 59)},DecS={0, 59} WHERE TargetCoordinates_Id = {target_coordinates_id};      
    """
        db_cursor.execute(sql)
        test_db_connection.commit()


def create_empty_test_database(test_db_connection: connect, test_db_name: str) -> None:
    """
    Create an empty test database.

    If the database exists already, it is removed first. The name of the test database
    must start with "test".

    Parameters
    ----------
    test_db_connection
        The test database connection.
    test_db_name
        The test database name, which must start with "test".

    Returns
    -------
        None
    """

    if not test_db_name.startswith("test"):
        raise ValueError("The test database name must start with \"test\".")

    try:
        with test_db_connection.cursor() as cur:
            # Delete an existing database
            drop_query = f"DROP DATABASE IF EXISTS %(db_name)s"
            cur.execute(drop_query, {"db_name": test_db_name})

            # Create the database
            create_query = f"CREATE DATABASE %(db_name)s"
            cur.execute(create_query, {"db_name": test_db_name})
    finally:
        test_db_connection.commit()


def update_sensitive_info(test_db_connection: connect) -> None:
    # !!! INITIATE A TRANSACTION !!!
    try:
        test_db_connection.begin()
        with test_db_connection.cursor() as cur:
            cur.execute(update_investigators(test_db_connection, cur))
            cur.execute(update_pipt_users_query(test_db_connection, cur))
            cur.execute(update_target_coordinates_query(test_db_connection, cur))

    except Exception as e:
        print("Exception occurred:{}".format(e))
    finally:
        test_db_connection.commit()
        test_db_connection.close()


def dump_database(db_user, db_password, db_host, db_name, result_file):
    script_dir = os.path.dirname(os.path.realpath(__file__))

    dump_file = script_dir + "/sdb_copy.sql"

    # Dumping the main database
    os.system(
        f"mysqldump -u {db_user} --password {db_password} -h {db_host} "
        f"--default-character-set=utf8 --routines --ignore-table=bumping_sdb.log {db_name} "
        f"--result-file {result_file}"
    )


@click.command()
@click.option('--main-db-host', type=str, help="The database to be dumped for this script it is the SDB.")
@click.option('--main-db-user', type=str, help="The main database user.")
@click.option('--main-db-name', type=str, help="The main database name.")
@click.option('--test-db-host', type=str, help="The test database host.")
@click.option('--test-db-user', type=str, help="The test database host.")
@click.option('--test-db-name', type=str, help="This is a new database for testing the name should start with test."
                                               "")
@click.option('--main-db-password', prompt="Enter main database password:", hide_input=True, confirmation_prompt=False,
                type=str)
@click.option('--test-db-password', prompt="Enter test database password:", hide_input=True, confirmation_prompt=False,
              type=str)
def cli(
        main_db_host,
        main_db_user,
        main_db_name,
        test_db_host,
        test_db_user,
        test_db_name,
        main_db_password,
        test_db_password,
):
    # Connect to the newly created test database
    test_db_connection = connect(host=test_db_host, user=test_db_user, password=test_db_password, db=test_db_name,
                                 port=3306)

    script_dir = os.path.dirname(os.path.realpath(__file__))

    dump_file = script_dir + "/sdb_copy.sql"

    # Dumping the main database
    dump_database(
        db_user=main_db_user,
        db_password=main_db_password,
        db_host=main_db_host,
        db_name=main_db_name,
        result_file=dump_file
    )

    # create the test database
    create_empty_test_database(test_db_connection, test_db_name)

    # importing mysql dump file
    os.system(
        f"mysql -u {test_db_user} --password='{test_db_password}' -h {test_db_host} "
        f"--default-character-set=utf8 {test_db_name} < {dump_file}"
    )
    # Remove the test database
    os.system(f"rm {dump_file}")

    # Update the test database
    update_sensitive_info(test_db_connection)
