from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    API_V1_STR: Optional[str] = "/api/v1"
    PROJECT_NAME: Optional[str] = "Notifications Service"
    HOST: Optional[str] = "0.0.0.0"
    PORT: Optional[int] = 5006
    DEBUG: Optional[bool] = True

    DB_URL: Optional[str] = (
        "postgresql://youssef:password@postgresdb:5432/pms_notifications_db"
    )
    BROKER_URL: Optional[str] = "amqp://guest:guest@rabbitmq:5672//"
    RABBITMQ_HOST: Optional[str] = "rabbitmq"
    RABBITMQ_PORT: Optional[int] = 5672
    RABBITMQ_USER: Optional[str] = "guest"
    RABBITMQ_PASSWORD: Optional[str] = "guest"

    SMTP_HOSTNAME: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: Optional[int] = 587
    SMTP_START_TLS: Optional[bool] = False
    SMTP_USE_TLS: Optional[bool] = False
    SMTP_USERNAME: Optional[str] = "your_email@gmail.com"
    SMTP_PASSWORD: Optional[str] = "your_password"


settings = Settings()
