from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr, field_validator
from typing import Any
from functools import lru_cache


@lru_cache()
def get_settings(env_file: str = ".env"):
    """
    Creates a cached instance of the settings.

    Args:
        emv_file (str): Environment file to get the settings from.
            Defaults to '.env'

    Returns:
        Settings: Settings object
    """
    # print(f"Creating settings from file: {env_file}")
    return Settings(_env_file=env_file, _env_file_encoding="utf-8")


class Settings(BaseSettings):
    # --- Auth Settings ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Initial Admin Settings ---
    FIRST_ADMIN_EMAIL: EmailStr
    FIRST_ADMIN_PASSWORD: str

    # --- Database Settings ---
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    @field_validator(
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_SERVER",
        mode="before",
    )
    @classmethod
    def strip_whitespace(cls, v: Any) -> Any:
        """Strip whitespace from database connection fields."""
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Any, info) -> Any:
        # If DATABASE_URL is already provided in .env, use it
        if isinstance(v, str) and v:
            return v
        # Otherwise, build it from components (useful for local vs docker)
        user = info.data.get("POSTGRES_USER")
        password = info.data.get("POSTGRES_PASSWORD")
        server = info.data.get("POSTGRES_SERVER")
        port = info.data.get("POSTGRES_PORT")
        db = info.data.get("POSTGRES_DB")

        return f"postgresql://{user}:{password}@{server}:{port}/{db}".strip()

    # This will be populated by the env var if provided,
    # otherwise we will build it in the validator above
    DATABASE_URL: str | None = None

    # Configuration
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )
