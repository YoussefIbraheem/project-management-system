import sqlite3
import pytest
import os

from flask_jwt_extended import JWTManager, create_access_token
from app import create_app, settings

os.environ["DB_URL"] = "sqlite:///:memory:"

class DummyModel:
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)
            
    def model_dump(self):
        return self.__dict__


@pytest.fixture
def app():
    os.environ["DB_URL"] = "sqlite:///:memory:"
    from app.db.database import create_tables

    flask_app = create_app()
    flask_app.config["TESTING"] = True
    flask_app.config["JWT_SECRET_KEY"] = settings.JWT_TEST_SECRET_KEY
    flask_app.config["JWT_ALGORITHM"] = "HS256"

    JWTManager(flask_app)
    create_tables()

    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Generate a valid JWT token and return it as Authorization headers."""
    with app.app_context():
        token = create_access_token(identity="10")  # default identity; override per test if needed
        return {"Authorization": f"Bearer {token}"}