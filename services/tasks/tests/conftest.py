import os

import pytest
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
os.environ.setdefault("PORT", "5000")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("API_V1_PREFIX", "/api/v1")

from datetime import datetime, timezone

from app import create_app
from app.db import database as db_module
from app.models import Base, Board, BoardColumn, Project, ProjectMember, Task
from app.models.project_member import MemberRole


@pytest.fixture()
def engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture()
def session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@pytest.fixture()
def db_session(session_factory):
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def app(session_factory, monkeypatch):
    monkeypatch.setattr(db_module, "SessionLocal", session_factory)
    test_app = create_app()
    test_app.config.update(
        TESTING=True, JWT_SECRET_KEY="test-secret", SECRET_KEY="test-secret"
    )
    return test_app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_headers(app):
    def _make(identity="user-1"):
        with app.app_context():
            token = create_access_token(identity=identity)
        return {"Authorization": f"Bearer {token}"}

    return _make


@pytest.fixture()
def seeded_data(db_session):
    project = Project(name="Alpha", description="Project Alpha")
    db_session.add(project)
    db_session.flush()

    member = ProjectMember(
        project_id=project.id, user_id="user-1", role=MemberRole.ADMIN.db_value
    )
    board = Board(name="Board 1", description="Main board", project_id=project.id)
    db_session.add_all([member, board])
    db_session.flush()

    todo = BoardColumn(
        board_id=board.id, slug="todo", label="To Do", status_group="pending"
    )
    doing = BoardColumn(
        board_id=board.id, slug="doing", label="Doing", status_group="in_progress"
    )
    db_session.add_all([todo, doing])
    db_session.flush()

    task = Task(
        title="Task 1",
        description="Task description",
        column_id=todo.id,
        priority="low",
        due_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        creator_id="user-1",
        board_id=board.id,
    )
    db_session.add(task)
    db_session.commit()

    return {
        "project": project,
        "member": member,
        "board": board,
        "todo": todo,
        "doing": doing,
        "task": task,
    }
