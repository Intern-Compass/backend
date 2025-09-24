from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr
from typing import Annotated


class Settings(BaseSettings):
    DB_URL: str
    FRONTEND_URL: str

    SECRET_KEY: str
    ALGO: str

    # Email Settings
    SMTP_SENDER_NAME: str
    SMTP_SENDER_EMAIL: Annotated[str, EmailStr]
    SMTP_USERNAME: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_PASSWORD: str

    USE_ML_MATCHING: bool
    RATE_LIMIT_ENABLED: bool

    model_config = SettingsConfigDict(
        env_file=".env",
    )


settings = Settings()
