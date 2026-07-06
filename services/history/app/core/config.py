from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    API_V1_STR: Optional[str] = "/api/v1"
    PROJECT_NAME: Optional[str] = "History Service"
    HOST: Optional[str] = "0.0.0.0"
    PORT: Optional[int] = 5006
    DEBUG: Optional[bool] = True

    MONGO_DB_URL: Optional[str] = ""
    MONGO_DB_NAME: Optional[str] = "history_db"

    SECRET_KEY: Optional[str] = ""
    ALGORITHM: Optional[str] = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = 30

    CELERY_BROKER_URL: Optional[str] = "amqp://guest:guest@rabbitmq:5672//"
    CELERY_RESULT_BACKEND: Optional[str] = "redis://redis:6379/0"
    ALLOW_INVALID_CERTS: Optional[bool] = False


settings = Settings()
