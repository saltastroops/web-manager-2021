from pymysql import connect

from tests.sdb_sensitive import (
    get_all_investigator_ids,
    get_all_pipt_user_ids,
    get_all_target_coordinates_id,
    update_investigators_query,
    update_pipt_users_query,
    update_target_coordinates_query
)


def clean_test_database(test_db_connection: connect, database_name: str) -> None:
    """
    The function drop and create the database which is provided.
    it will only drop the database if the name starts with test

    Parameters
    ----------
    test_db_connection
        The test database connection
    database_name
        The database name in question the name should starts with the word test.

    Returns
    -------
        None
    """

    if not database_name.startswith("test"):
        raise ValueError("The test database name should start with test.")
    try:
        with test_db_connection.cursor() as cur:
            # Create a cursor object
            cur = test_db_connection.cursor()

            # SQL Statement to delete a database
            drop_query = f"DROP DATABASE IF EXISTS {database_name};"

            # SQL Statement to create a database
            create_query = f"CREATE DATABASE IF NOT EXISTS {database_name}"

            # Execute the delete database SQL statement through the cursor instance
            cur.execute(drop_query)

            # Execute the create database SQL statement through the cursor instance
            cur.execute(create_query)

    except Exception as e:
        print("Exception occurred:{}".format(e))

    finally:
        test_db_connection.commit()


def update_test_database(test_db_connection: connect) -> None:
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
