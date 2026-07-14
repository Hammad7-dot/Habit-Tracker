"""
Application configuration.
Loads settings from environment variables / .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Habit Tracker API"
    ENV: str = "development"  # development | production
    DEBUG: bool = True

    # Database
    # Local dev default: SQLite file. In production, set DATABASE_URL to a
    # PostgreSQL connection string, e.g.
    # postgresql://user:password@host:5432/habit_tracker
    #
    # Render (and Heroku) inject DATABASE_URL with the legacy "postgres://"
    # scheme, which SQLAlchemy 2.x rejects — it must be "postgresql://".
    # The validator below rewrites it automatically so the same env var
    # Render provides can be used as-is, no manual editing needed.
    DATABASE_URL: str = "sqlite:///./habit_tracker.db"

    # JWT Auth
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_super_secret_key_please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS — set to the deployed frontend origin(s) in production, e.g.
    # CORS_ORIGINS=https://your-app.vercel.app
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:5500,http://localhost:5500"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("DATABASE_URL")
    @classmethod
    def _normalize_database_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    @property
    def is_production(self) -> bool:
        return self.ENV.lower() == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.is_production and settings.SECRET_KEY == "CHANGE_ME_IN_PRODUCTION_super_secret_key_please":
        raise RuntimeError(
            "SECRET_KEY is still the default value. Set a real SECRET_KEY "
            "environment variable before running with ENV=production."
        )
    return settings


settings = get_settings()
