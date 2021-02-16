import os
import click
from pymysql import connect, cursors

from tests.sdb_sensitive import (
    get_all_investigator_ids,
    get_all_pipt_user_ids,
    get_all_target_coordinates_id,
    update_investigators_query,
    update_pipt_users_query,
    update_target_coordinates_query
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

    MAIN_DB_HOST = main_db_host
    MAIN_DB_USER = main_db_user
    MAIN_DB_PASSWORD = main_db_password
    MAIN_DB_NAME = main_db_name

    TEST_DB_HOST = test_db_host
    TEST_DB_USER = test_db_user
    TEST_DB_PASSWORD = test_db_password
    TEST_DB_NAME = test_db_name

    host_connection = connect(host=TEST_DB_HOST, user=TEST_DB_USER, password=TEST_DB_PASSWORD,
                              charset="utf8mb4", cursorclass=cursors.DictCursor)

# ________________________________________Start Create a dump SDB_______________________________________________________
    script_dir = os.path.dirname(os.path.realpath(__file__))

    dump_file = script_dir + "/sdb_copy.sql"

    os.system(
        f"mysqldump -u {MAIN_DB_USER} --password {MAIN_DB_PASSWORD} -h {MAIN_DB_HOST} "
        f"--default-character-set=utf8 --routines --ignore-table=bumping_sdb.log {MAIN_DB_NAME} "
        "--result-file sdb_copy.sql"
    )

    # clean the test database
    create_empty_test_database(host_connection, TEST_DB_NAME)

    # import mysql dump file
    os.system(
        f"mysql -u {TEST_DB_USER} --password='{TEST_DB_PASSWORD}' -h {TEST_DB_HOST} "
        f"--default-character-set=utf8 {TEST_DB_NAME} < {dump_file}"
    )
    os.system(f"rm {dump_file}")
# ________________________________________End Create a dump SDB_________________________________________________________

# ________________________________________Start test Database update____________________________________________________
    # Connect to the newly created test database
    test_db_connection = connect(host=TEST_DB_HOST, user=TEST_DB_USER, passwd=TEST_DB_PASSWORD, db=TEST_DB_NAME,
                                 port=3306)

    # Collecting the ids to update
    investigators = get_all_investigator_ids(test_db_connection)
    pipt_users = get_all_pipt_user_ids(test_db_connection)
    target_coordinates = get_all_target_coordinates_id(test_db_connection)

    # !!! INITIATE A TRANSACTION !!!
    try:
        test_db_connection.begin()
        with test_db_connection.cursor() as cur:
            cur.execute(update_investigators_query(investigators))
            cur.execute(update_pipt_users_query(pipt_users))
            cur.execute(update_target_coordinates_query(target_coordinates))

    except Exception as e:
        print("Exception occurred:{}".format(e))
    finally:
        test_db_connection.commit()
        test_db_connection.close()

# ________________________________________End test Database update______________________________________________________


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
