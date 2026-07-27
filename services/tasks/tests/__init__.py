import os

from flask_jwt_extended import create_access_token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("DB_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("LOGGING_LEVEL", "CRITICAL")
os.environ.setdefault("SERVICE_NAME", "tasks")
os.environ.setdefault("SERVICE_VERSION", "test")
os.environ.setdefault("HOST", "127.0.0.1")
os.environ.setdefault("PORT", "8080")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("API_V1_PREFIX", "/api/v1")

from app import create_app
from app.db import database as db_module
from app.models import Base


class DummyModel:
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)

    def model_dump(self):
        return self.__dict__


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    future=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
db_module.SessionLocal = SessionLocal


import pytest


@pytest.fixture
def app():
    flask_app = create_app()
    flask_app.config.update(
        TESTING=True,
        JWT_SECRET_KEY="test-secret",
        SECRET_KEY="test-secret",
    )
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    def _make(identity="10"):
        with app.app_context():
            token = create_access_token(identity=identity)
        return {"Authorization": f"Bearer {token}"}

    return _make
