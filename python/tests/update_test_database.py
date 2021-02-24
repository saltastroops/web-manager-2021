import asyncio
import os
import pathlib
import subprocess
import tempfile
from random import randint
from typing import List

import click
import pydantic
from aiomysql import connect
from faker import Faker

fake = Faker()
Faker.seed(4321)


class Database(pydantic.BaseModel):
    host: str
    database: str
    username: str
    password: str


class TargetCoordinates(pydantic.BaseModel):
    """Right ascension and declination."""

    id: int
    ra_h: int
    ra_m: int
    ra_s: float
    dec_sign: str
    dec_deg: int
    dec_m: int
    dec_s: float


async def get_all_investigator_ids(test_db_connection: connect) -> List[int]:
    """
    Get all the investigators ids.

    Parameters
    ----------
    test_db_connection:
        The test database connection.

    Returns
    -------
    list
        The List of investigators ids.

    """

    with test_db_connection.cursor() as cur:
        cur.execute("SELECT Investigator_Id FROM Investigator")
        results = await cur.fetchall()
        return [investigator[0] for investigator in results]


async def get_all_pipt_user_ids(test_db_connection: connect) -> List[int]:
    """
    Get all the PIPT user ids.

    Parameters
    ----------
    test_db_connection:
        The test database connection.

    Returns
    -------
    list
        The List of PIPT user ids.

    """

    with test_db_connection.cursor() as cur:
        cur.execute("SELECT PiptUser_Id FROM PiptUser")
        results = await cur.fetchall()
        return [pipt_user[0] for pipt_user in results]


async def get_all_target_coordinate_ids(test_db_connection: connect) -> List[int]:
    """
    Get all the target coordinate ids.

    Parameters
    ----------
    test_db_connection:
        The database connection that have table TargetCoordinates as the table.

    Returns
    -------
    list
        The list of target coordinates ids.

    """

    with test_db_connection.cursor() as cur:
        cur.execute("SELECT TargetCoordinates_Id FROM TargetCoordinates")
        results = await cur.fetchall()
        return [target_coordinates[0] for target_coordinates in results]


async def update_investigators(test_db_connection: connect) -> None:
    """
    Replace the sensitive data in the Investigator table with fake data.

    Parameters
    ----------
    test_db_connection
        The test database connection.

    """

    investigator_ids = await get_all_investigator_ids(test_db_connection)
    data = [
        (
            fake.first_name(),
            fake.last_name(),
            fake.email(),
            fake.phone_number(),
            investigator_id,
        )
        for investigator_id in investigator_ids
    ]
    sql = f"""
UPDATE Investigator
SET  FirstName = %s, Surname = %s, Email = %s, Phone = %s
WHERE Investigator_Id = %s;
    """
    cursor = await test_db_connection.cursor()
    await cursor.executemany(sql, data)


async def update_pipt_users(test_db_connection: connect) -> None:
    """
    Replace the sensitive data in the PiptUser table with fake data.

    Parameters
    ----------
    test_db_connection
        The test database connection.

    """

    pipt_user_ids = await get_all_pipt_user_ids(test_db_connection)
    passphrase = os.getenv("TEST_DB_USER_PASSPHRASE")
    data = [
        (fake.user_name(), f"user-{pipt_user_id}-{passphrase}", pipt_user_id)
        for pipt_user_id in pipt_user_ids
    ]
    sql = f"""
UPDATE PiptUser
SET Username = %s, Password = MD5(%s)
WHERE PiptUser_Id = %s;
    """
    cursor = await test_db_connection.cursor()
    await cursor.executemany(sql, data)


def fake_target_coordinates(target_coordinates_id: int) -> TargetCoordinates:
    """Generate fake target coordinates."""
    dec_deg = randint(-75, 10)
    sign = "-" if dec_deg < 0 else "+"
    return TargetCoordinates(
        id=target_coordinates_id,
        ra_h=randint(0, 23),
        ra_m=randint(0, 59),
        ra_s=randint(0, 59),
        dec_sign=sign,
        dec_deg=abs(dec_deg),
        dec_m=randint(0, 59),
        dec_s=randint(0, 59),
    )


async def update_target_coordinates(test_db_connection: connect) -> None:
    """
    Replace the sensitive data in the TargetCoordinates table with fake data.

    Parameters
    ----------
    test_db_connection
        A test database connection.

    """

    target_coordinate_ids = await get_all_target_coordinate_ids(test_db_connection)
    target_coordinate_list = [
        fake_target_coordinates(target_coordinate_id)
        for target_coordinate_id in target_coordinate_ids
    ]
    data = [
        (tc.ra_h, tc.ra_m, tc.ra_s, tc.dec_sign, tc.dec_deg, tc.dec_m, tc.dec_s, tc.id)
        for tc in target_coordinate_list
    ]
    sql = f"""
UPDATE TargetCoordinates
SET RaH=%s, RaM=%s, RaS=%s, DecSign=%s, DecD=%s, DecM=%s, DecS=%s
WHERE TargetCoordinates_Id=%s;      
    """
    cursor = await test_db_connection.cursor()
    await cursor.executemany(sql, data)


async def create_empty_test_database(
    test_db_connection: connect, test_db_name: str
) -> None:
    """
    Create an empty test database.

    If the database exists already, it is removed first. The name of the test database
    must start with "test".

    Parameters
    ----------
    test_db_connection
        A test database connection.
    test_db_name
        The test database name, which must start with "test".

    """

    if not test_db_name.startswith("test"):
        raise ValueError('The test database name must start with "test".')

    # Delete an existing database
    async with test_db_connection.cursor() as cur:
        drop_query = f"DROP DATABASE IF EXISTS `{test_db_name}`"
        await cur.execute(drop_query)

        # Create the database
        create_query = f"CREATE DATABASE `{test_db_name}`"
        await cur.execute(create_query)


async def replace_sensitive_info(test_db_connection: connect) -> None:
    """Replace sensitive information in the test database with fake data."""
    await update_investigators(test_db_connection)
    await update_pipt_users(test_db_connection)
    await update_target_coordinates(test_db_connection)


def dump_database(db_user, db_password, db_host, db_name, dump_file):
    subprocess.run(
        [
            "mysqldump",
            "-u",
            db_user,
            f"-p{db_password}",
            "-h",
            db_host,
            "--default-character-set=utf8",
            "--routines",
            "--single-transaction",
            "-r",
            dump_file,
            db_name,
        ]
    )


async def create_test_database(main_db: Database, test_db: Database) -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        dump_file = pathlib.Path(tmp_dir) / "dump.sql"

        # # dump the main database
        # dump_database(
        #     db_user=main_db.username,
        #     db_password=main_db.password,
        #     db_host=main_db.host,
        #     db_name=main_db.database,
        #     dump_file=dump_file
        # )

        dump_file = "/Users/christian/Desktop/sdb.sql"

        # create the test database
        # Note: The name of the test database name must not be passed, as the database
        #       might not exist yet.
        test_db_server_connection = await connect(
            host=test_db.host, user=test_db.username, password=test_db.password
        )
        await create_empty_test_database(test_db_server_connection, test_db.database)
        test_db_server_connection.close()

        # importing mysql dump file
        os.system(
            [
                f"mysql -u {test_db.username} -p{test_db.password} -h {test_db.host} "
                f"--default-character-set=utf8 {test_db.database} < {dump_file}"
            ]
        )
        #
        # # Connect to the newly created test database
        #
        # script_dir = os.path.dirname(os.path.realpath(__file__))
        #
        # dump_file = script_dir + "/sdb_copy.sql"
        #
        # # Remove the test database
        # os.system(f"rm {dump_file}")
        #
        # # Update the test database

        # connect to the test database (now we have to pass the name)
        test_db_connection = await connect(
            host=test_db.host, user=test_db.username, password=test_db.password
        )

        # replace_sensitive_info(test_db_connection)


@click.command()
@click.option(
    "--main-db-host",
    type=str,
    help="The database to be dumped for this script it is the SDB.",
)
@click.option("--main-db-user", type=str, help="The main database user.")
@click.option("--main-db-name", type=str, help="The main database name.")
@click.option("--test-db-host", type=str, help="The test database host.")
@click.option("--test-db-user", type=str, help="The test database host.")
@click.option(
    "--test-db-name",
    type=str,
    help="This is a new database for testing the name should start with test." "",
)
@click.option(
    "--main-db-password",
    prompt="Enter main database password:",
    hide_input=True,
    confirmation_prompt=False,
    type=str,
)
@click.option(
    "--test-db-password",
    prompt="Enter test database password:",
    hide_input=True,
    confirmation_prompt=False,
    type=str,
)
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
    main_db = Database(
        host=main_db_host,
        database=main_db_name,
        username=main_db_user,
        password=main_db_password,
    )
    test_db = Database(
        host=test_db_host,
        database=test_db_name,
        username=test_db_user,
        password=test_db_password,
    )

    asyncio.run(create_test_database(main_db, test_db))


if __name__ == "__main__":
    cli()
