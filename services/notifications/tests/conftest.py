from pathlib import Path
import sys

import pytest
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# Import the ORM models so SQLModel.metadata knows about every table.
from app.models.email_log import EmailLog  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.user_replica import UserReplica  # noqa: F401

from app.db import database as db_module
from app.services import email_log_service, notification_service, user_replica_service


@pytest.fixture()
def engine():
    test_engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(test_engine, "connect")
    def _enable_foreign_keys(dbapi_connection, connection_record):  # noqa: ARG001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture()
def session(engine):
    with Session(engine) as db_session:
        yield db_session


@pytest.fixture(autouse=True)
def patch_notification_db(engine, monkeypatch):
    monkeypatch.setattr(db_module, "engine", engine)
    monkeypatch.setattr(notification_service, "engine", engine)
    monkeypatch.setattr(user_replica_service, "engine", engine)
    monkeypatch.setattr(email_log_service, "engine", engine)
    yield
