import os

from pydantic import BaseSettings


def _get_env_file() -> str:
    """`The environment variable file name for the mode the server is running in."""
    mode = os.getenv("MODE")
    if mode is None:
        raise ValueError(
            "The MODE environment variable is not set. Please refer to "
            "the documentation for more details."
        )

    mode = mode.lower()
    if mode == "production":
        return ".env"
    elif mode == "test":
        return ".env.test"
    else:
        raise ValueError(
            "The MODE environment variable has an unsupported value. "
            "Please refer to the documentation for the available values."
        )


class Settings(BaseSettings):
    """
    Settings for the Web Manager.

    Every setting must be defined as an environment variable (or in an .env file at the
    root level of the project). The environment variable names may be in uppercase.
    """

    # Base directory for proposal content
    proposals_base_dir: str

    # DSN for the SALT Science Database
    sdb_dsn: str

    # Secret key for encoding JWT tokens.
    secret_key: str

    class Config:
        env_file = _get_env_file()
