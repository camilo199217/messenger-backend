from functools import lru_cache
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    database_url: str

    jwt_secret: str
    jwt_algorithm: Optional[str] = "HS256"
    jwt_expiration: Optional[int] = 30

    LOGIN_ATTEMPTS_ENABLED: Optional[bool] = False
    LOGIN_ATTEMPTS_MAX: Optional[int] = 5

    ORIGINS: Optional[list[str]] = [
        "http://messenger.localhost:9000",
        "http://localhost:9000",
    ]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings():
    return Settings()
