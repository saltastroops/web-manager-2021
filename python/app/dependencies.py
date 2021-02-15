from functools import lru_cache

from app.settings import Settings


@lru_cache()  # for performance reasons, as the function is called for every request
def get_settings() -> Settings:
    """Get the Web Manager settings."""
    return Settings()
