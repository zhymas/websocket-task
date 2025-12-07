from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

class RedisSettings(BaseSettings):
    host: str = Field("localhost", alias="REDIS_HOST")
    port: int = Field(6379, alias="REDIS_PORT")
    password: str = Field("redispassword", alias="REDIS_PASSWORD")


class Settings(BaseSettings):
    redis_settings: RedisSettings = RedisSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()