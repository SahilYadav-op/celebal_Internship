from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings, loaded from environment variables or a .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Quiz Backend Management API"
    # default is local sqlite, change this in .env to use postgres/mysql
    DATABASE_URL: str = "sqlite:///./quiz.db"


settings = Settings()
