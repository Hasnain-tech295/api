from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Book API"
    app_version: str = "0.4.0"
    debug: bool = False
    database_url: str = "sqlite:///./books.db"
    secret_key: str = "change-me"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()