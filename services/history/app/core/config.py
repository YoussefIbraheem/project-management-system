
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    API_PREFIX: str | None = "/api/v1"
    PROJECT_NAME: str | None = "History Service"
    HOST: str | None = "0.0.0.0"
    PORT: int | None = 5006
    DEBUG: bool | None = True

    MONGO_DB_URL: str | None = ""
    MONGO_DB_NAME: str | None = "history_db"

    JWT_SECRET_KEY: str | None = ""
    ALGORITHM: str | None = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int | None = 30

    CELERY_BROKER_URL: str | None = "amqp://guest:guest@rabbitmq:5672//"
    RABBITMQ_BROKER_URL: str | None = "amqp://guest:guest@rabbitmq:5672//"
    CELERY_RESULT_BACKEND: str | None = "redis://redis:6379/0"
    ALLOW_INVALID_CERTS: bool | None = False


settings = Settings()
