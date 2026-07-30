from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    API_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Notifications Service"
    HOST: str = "0.0.0.0"
    PORT: int = 5006
    DEBUG: bool = True

    DB_URL: str = "postgresql://youssef:password@postgresdb:5432/pms_notifications_db"
    BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    JWT_SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"

    SMTP_HOSTNAME: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_START_TLS: bool = False
    SMTP_USE_TLS: bool = False
    SMTP_USERNAME: str = "your_email@gmail.com"
    SMTP_PASSWORD: str = "your_password"
    DNS_TIMEOUT: float = 5
    SMTP_VERIFY_TIMEOUT: float = 8
    SMTP_MAX_ATTEMPTS: int = 3

    DLX_TTL: int = 300000


settings = Settings()
