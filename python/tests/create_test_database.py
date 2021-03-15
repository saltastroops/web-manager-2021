import asyncio
import os
import pathlib
import random
import subprocess
import tempfile
from random import randint
from typing import Dict, List

import click
import pydantic
from aiomysql import connect
from faker import Faker

from tests.update_permissions import create_known_users

fake = Faker()
Faker.seed(4321)
random.seed(4321)


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


class InvestigatorDetails(pydantic.BaseModel):
    """Investigator details."""

    id: int
    first_name: str
    last_name: str
    email: str
    phone: str


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

    async with test_db_connection.cursor() as cur:
        await cur.execute("SELECT Investigator_Id FROM Investigator")
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

    async with test_db_connection.cursor() as cur:
        await cur.execute("SELECT PiptUser_Id FROM PiptUser")
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

    async with test_db_connection.cursor() as cur:
        await cur.execute("SELECT TargetCoordinates_Id FROM TargetCoordinates")
        results = await cur.fetchall()
        return [target_coordinates[0] for target_coordinates in results]


_used_email_users: Dict[str, int] = {}


def fake_investigator_details(investigator_id: int) -> InvestigatorDetails:
    """Return fake investigator details."""

    global _used_email_users

    first_name = fake.first_name()
    last_name = fake.last_name()
    email_user = f"{first_name.lower()}.{last_name.lower()}"
    if email_user in _used_email_users:
        _used_email_users[email_user] += 1
        email = (
            f"{first_name.lower()}.{last_name.lower()}"
            f"{_used_email_users.get(email_user)}@email.com"
        )
    else:
        _used_email_users[email_user] = 1
        email = f"{first_name.lower()}.{last_name.lower()}@email.com"

    return InvestigatorDetails(
        id=investigator_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=fake.phone_number(),
    )


async def update_investigators(test_db_connection: connect) -> None:
    """
    Replace the sensitive data in the Investigator table with fake data.

    Parameters
    ----------
    test_db_connection
        The test database connection.

    """

    investigator_ids = await get_all_investigator_ids(test_db_connection)
    investigator_details_list = [
        fake_investigator_details(investigator_id)
        for investigator_id in investigator_ids
    ]
    data = [
        (
            details.first_name,
            details.last_name,
            details.email,
            details.phone,
            details.id,
        )
        for details in investigator_details_list
    ]
    sql = """
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
    sql = """
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
        ra_s=60 * random.random(),
        dec_sign=sign,
        dec_deg=abs(dec_deg),
        dec_m=randint(0, 59),
        dec_s=60 * random.random(),
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
    sql = """
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


def dump_database(
    db_user: str, db_password: str, db_host: str, db_name: str, dump_file: pathlib.Path
) -> None:
    subprocess.run(
        [
            "mysqldump",
            "-u",
            db_user,
            f"-p{db_password}",
            "-h",
            db_host,
            "--default-character-set=utf8",
            "--single-transaction",
            "-r",
            dump_file,
            f"--ignore-table={db_name}.V_P1ProposalInstruments",
            f"--ignore-table={db_name}.V_ProposalInstruments",
            db_name,
        ]
    )


async def create_test_database(source_db: Database, test_db: Database) -> None:
    """Create the test database."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        dump_file = pathlib.Path(tmp_dir) / "dump.sql"

        # dump the source database
        dump_database(
            db_user=source_db.username,
            db_password=source_db.password,
            db_host=source_db.host,
            db_name=source_db.database,
            dump_file=dump_file,
        )

        # create the test database
        # Note: The name of the test database name must not be passed, as the database
        #       might not exist yet.
        test_db_server_connection = await connect(
            host=test_db.host, user=test_db.username, password=test_db.password
        )
        await create_empty_test_database(test_db_server_connection, test_db.database)
        test_db_server_connection.close()

        # import the MySQL dump file
        with open(dump_file) as f:
            subprocess.run(
                [
                    "mysql",
                    "-u",
                    test_db.username,
                    f"-p{test_db.password}",
                    "-h",
                    test_db.host,
                    "--default-character-set=utf8",
                    test_db.database,
                ],
                stdin=f,
            )

        # connect to the new test database (now we have to pass the name)...
        test_db_connection = await connect(
            host=test_db.host,
            user=test_db.username,
            password=test_db.password,
            db=test_db.database,
        )

        # ... and get rid of the sensitive information
        try:
            await replace_sensitive_info(test_db_connection)
            await create_known_users(test_db_connection)
        except Exception as e:
            await test_db_connection.rollback()
            raise e
        else:
            await test_db_connection.commit()

        test_db_connection.close()


@click.command()
@click.option(
    "--source-db-host",
    type=str,
    required=True,
    help="The source database host.",
)
@click.option(
    "--source-db-user",
    type=str,
    required=True,
    help="The username of the source database user account.",
)
@click.option(
    "--source-db-password",
    prompt="Enter the source database password:",
    hide_input=True,
    confirmation_prompt=False,
    type=str,
    help="The password of the source database user account.",
)
@click.option(
    "--source-db-name", type=str, required=True, help="The name of the source database."
)
@click.option("--test-db-host", type=str, required=True, help="The test database host.")
@click.option(
    "--test-db-user",
    type=str,
    required=True,
    help="The username of the test database user account.",
)
@click.option(
    "--test-db-password",
    prompt="Enter the test database password:",
    hide_input=True,
    confirmation_prompt=False,
    type=str,
    help="The password of the test database user account.",
)
@click.option(
    "--test-db-name",
    type=str,
    required=True,
    help="The name of the test database. This name must start with 'test'.",
)
def cli(
    source_db_host: str,
    source_db_user: str,
    source_db_password: str,
    source_db_name: str,
    test_db_host: str,
    test_db_user: str,
    test_db_password: str,
    test_db_name: str,
) -> None:
    """
    Generate a test database with sensitive information replaced.

    createtestdb copies a source database to a test database, which is created if need.
    The source database must be a copy of the SALT Science Database.

    The test database is deleted and recreated if it exists already. Sensitive content
    such as names, contact details and target coordinates are replaced with fake values.

    The fake values are deterministic; repeated uses of the command will always give the
    same fake values, as long as the original database does not change.

    The name of the test database must start with "test".

    Even though the most sensitive information in the database is replaced, the
    resulting test database should still be considered confidential, and should only be
    shared with people you would share the source database with.
    """

    source_db = Database(
        host=source_db_host,
        database=source_db_name,
        username=source_db_user,
        password=source_db_password,
    )
    test_db = Database(
        host=test_db_host,
        database=test_db_name,
        username=test_db_user,
        password=test_db_password,
    )

    asyncio.run(create_test_database(source_db, test_db))


if __name__ == "__main__":
    cli()
