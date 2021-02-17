import os
import random
from random import randint
from faker import Faker

from typing import List
from pymysql import connect


fake = Faker()


def get_all_investigator_ids(test_db_connection: connect) -> List[int]:
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
    investigator_ids = []
    with test_db_connection.cursor() as cur:
        cur.execute("SELECT Investigator_Id FROM Investigator")
        results = cur.fetchall()
        return [investigator[0] for investigator in results]


def get_all_pipt_user_ids(test_db_connection: connect) -> List[int]:
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
        results = cur.fetchall()
        return [pipt_user[0] for pipt_user in results]


def get_all_target_coordinates_id(test_db_connection: connect) -> List[int]:
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
        results = cur.fetchall()
        return [target_coordinate[0] for target_coordinate in results]


def update_investigators_query(investigator_ids: List[int]) -> str:
    """
    Generate a query that will update all the sensitive information from the Investigator table.

    Parameters
    ----------
    investigator_ids
        The investigator id

    Returns
    -------
        The query
    """
    sql = ""
    for investigator_id in investigator_ids:
        sql += f"""Update Investigator
SET  FirstName = {fake.first_name()}, Surname = {fake.last_name()}, Email = {fake.email()}, Phone = {fake.phone_number()}
WHERE Investigator_Id = {investigator_id};
        """
    return sql


def update_pipt_users_query(pipt_user_ids: List[int]) -> str:
    """
    Generate a query that will update all the sensitive information from the PIPT user table.

    Parameters
    ----------
    pipt_user_ids
        The PIPT user ids

    Returns
    -------
        The query
    """
    sql = ""
    for pipt_user_id in pipt_user_ids:
        sql += f"""UPDATE PiptUser
SET Username = user-{fake.user_name()}, Password = MD5(user-{pipt_user_id}-{os.getenv("SECRET_PASS")})
WHERE PiptUser_Id = {pipt_user_id};
        """
    return sql


def update_target_coordinates_query(target_coordinates_ids: List[int]) -> str:
    """
    Generate a query that will update all the sensitive information from the target coordinates table.

    Parameters
    ----------
    target_coordinates_ids
        The target coordinates ids

    Returns
    -------
        The query
    """
    sql = ""
    for target_coordinates_id in target_coordinates_ids:
        sql += f"""UPDATE TargetCoordinates
SET RaH={randint(0, 23)},RaM={randint(0, 59)},RaS={randint(0, 59)},DecSign={random.choice(["+", "-"])},DecD={randint(0, 75)},DecM={randint(0, 59)},DecS={0, 59}
WHERE TargetCoordinates_Id = {target_coordinates_id};      
        """
    return sql
