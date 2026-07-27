from __future__ import annotations  # For forward references in type hints

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    """
    Configuration settings for the Tasks service.
    This class loads settings from environment variables with default values.
    Singleton pattern is used to ensure only one instance of settings is created.
    """

    # SYSTEM settings
    ENVIRONMENT: str = "development"
    LOGGING_LOCATION: str = "/var/log"
    LOGGING_LEVEL: str = "INFO"
    TIMEZONE: str = "UTC"

    # API settings
    API_PREFIX: str = "/api/v1"
    SERVICE_NAME: str = "tasks"
    SERVICE_VERSION: str = "0.1.0"
    JWT_SECRET_KEY: str = ""
    JWT_TEST_SECRET_KEY = "TESTSECRETKEY"
    JWT_DECODE_ALGORITHMS: str = "HS256"
    API_DOC_LOCATION = "./openapi.yaml"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    DEBUG: bool = True

    # Database settings
    DB_URL: str = "postgresql://postgres:password@localhost:5432/pms_tasks_db"

    # Broker URL
    BROKER_URL = "amqp://guest:guest@rabbitmq:5672/"

    _instance: Optional[Settings] = None

    def __post_init__(self):
        """Load from environment variables after initialization"""
        self.API_PREFIX = os.getenv("API_V1_PREFIX", self.API_PREFIX)
        self.SERVICE_NAME = os.getenv("SERVICE_NAME", self.SERVICE_NAME)
        self.SERVICE_VERSION = os.getenv("SERVICE_VERSION", self.SERVICE_VERSION)
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", self.JWT_SECRET_KEY)
        self.JWT_TEST_SECRET_KEY = os.getenv(
            "JWT_TEST_SECRET_KEY", self.JWT_TEST_SECRET_KEY
        )
        self.JWT_DECODE_ALGORITHMS = os.getenv(
            "JWT_DECODE_ALGORITHMS", self.JWT_DECODE_ALGORITHMS
        )
        self.HOST = os.getenv("HOST", self.HOST)
        self.PORT = int(os.getenv("PORT", self.PORT))
        self.API_DOC_LOCATION = os.getenv("API_DOC_LOCATION", self.API_DOC_LOCATION)
        self.DEBUG = os.getenv("DEBUG", str(self.DEBUG)).lower() == "true"
        self.LOGGING_LOCATION = os.getenv("LOGGING_LOCATION", self.LOGGING_LOCATION)
        self.LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", self.LOGGING_LEVEL)
        self.DB_URL = os.getenv("DB_URL", self.DB_URL)
        self.BROKER_URL = os.getenv("BROKER_URL", self.BROKER_URL)

    @classmethod
    def get_instance(cls) -> Settings:
        """get_instance

        Returns:
            Settings: The singleton instance of Settings.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
