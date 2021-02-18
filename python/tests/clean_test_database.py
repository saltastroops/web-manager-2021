from pymysql import connect

from tests.sdb_sensitive import (
    get_all_investigator_ids,
    get_all_pipt_user_ids,
    get_all_target_coordinates_id,
    update_investigators_query,
    update_pipt_users_query,
    update_target_coordinates_query
)


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
