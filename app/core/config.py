from functools import lru_cache
from pydantic_settings import BaseSettings,SettingsConfigDict


from pathlib import Path

# Project root directory (job-agent/)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = ROOT_DIR / ".env"


class Settings(BaseSettings):
    DATABASE_URL: str
    GROQ_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=(str(ENV_PATH), ".env"),
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()