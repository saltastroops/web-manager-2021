from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Settings for the Web Manager.

    Every setting must be defined as an environment variable (or in an .env file at the
    root level of the project). The environment variable names may be in uppercase.
    """

    # Secret key for encoding JWT tokens.
    secret_key: str

    class Config:
        env_file = ".env"
