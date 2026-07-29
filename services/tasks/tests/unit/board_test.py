
import pytest
from app.db.database import get_db_session
from app.models import Board, BoardColumn, Project, ProjectMember
from app.schemas.board_schema import BoardCreate, BoardUpdate
from app.security.actor import Actor
from app.security.roles import MemberRole
from app.services.board_service import (
    create_board,
    delete_board,
    delete_column,
    get_board_by_id,
    get_board_by_project,
    get_column,
    get_columns,
    update_board,
)
from shared.exceptions import NotFoundException


def _seed_board():
    with get_db_session() as db:
        project = Project(name="Test Project", description="Project for board tests")
        db.add(project)
        db.flush()

        member = ProjectMember(
            project_id=project.id, user_id="1", role=MemberRole.MANAGER.db_value
        )
        board = Board(name="Test Board", description="Test board", project_id=project.id)
        db.add_all([member, board])
        db.flush()

        todo = BoardColumn(
            board_id=board.id, slug="todo", label="To Do", status_group="pending"
        )
        doing = BoardColumn(
            board_id=board.id, slug="doing", label="Doing", status_group="in_progress"
        )
        done = BoardColumn(
            board_id=board.id, slug="done", label="Done", status_group="done"
        )
        db.add_all([todo, doing, done])
        db.commit()

        return {
            "project_id": project.id,
            "board_id": board.id,
            "todo_id": todo.id,
            "doing_id": doing.id,
            "done_id": done.id,
            "actor": Actor(user_id="1", is_superuser=True),
        }


def test_get_board_by_project_success():
    seeded = _seed_board()

    result = get_board_by_project(
        seeded["actor"], project_id=seeded["project_id"], limit=10, offset=0
    )

    assert len(result) >= 1
    assert any(b.id == seeded["board_id"] for b in result)


def test_get_board_by_project_with_pagination():
    seeded = _seed_board()

    result = get_board_by_project(
        seeded["actor"], project_id=seeded["project_id"], limit=5, offset=0
    )

    assert isinstance(result, list)


def test_get_board_by_id_success():
    seeded = _seed_board()

    result = get_board_by_id(seeded["actor"], board_id=seeded["board_id"])

    assert result.id == seeded["board_id"]
    assert result.name == "Test Board"


def test_get_board_by_id_not_found():
    seeded = _seed_board()

    with pytest.raises(NotFoundException):
        get_board_by_id(seeded["actor"], board_id=999)


def test_create_board_success():
    seeded = _seed_board()

    board_data = BoardCreate(
        name="New Board",
        description="New Board Description",
        project_id=seeded["project_id"],
        default_columns=False,
    )

    result = create_board(seeded["actor"], board_data)

    assert result.name == "New Board"
    assert result.description == "New Board Description"
    assert result.project_id == seeded["project_id"]


def test_create_board_with_default_columns():
    seeded = _seed_board()

    board_data = BoardCreate(
        name="Board with Columns",
        description="Test",
        project_id=seeded["project_id"],
        default_columns=True,
    )

    result = create_board(seeded["actor"], board_data)

    assert result.name == "Board with Columns"
    assert result.id is not None


def test_update_board_success():
    seeded = _seed_board()

    board_data = BoardUpdate(name="Updated Board", description="Updated Description")

    result = update_board(
        seeded["actor"],
        board_id=seeded["board_id"],
        board_data=board_data,
    )

    assert result.name == "Updated Board"
    assert result.description == "Updated Description"


def test_update_board_partial():
    seeded = _seed_board()

    partial_update = BoardUpdate(name="New Name", description=None)

    result = update_board(
        seeded["actor"],
        board_id=seeded["board_id"],
        board_data=partial_update,
    )

    assert result.name == "New Name"


def test_delete_board_success():
    seeded = _seed_board()

    result = delete_board(seeded["actor"], board_id=seeded["board_id"])

    assert result is True


def test_delete_board_not_found():
    seeded = _seed_board()

    with pytest.raises(NotFoundException):
        delete_board(seeded["actor"], board_id=999)


def test_get_columns_success():
    seeded = _seed_board()

    result = get_columns(seeded["actor"], board_id=seeded["board_id"])

    assert len(result) >= 1
    assert any(c.id == seeded["todo_id"] for c in result)


def test_get_column_success():
    seeded = _seed_board()

    result = get_column(
        seeded["actor"],
        board_id=seeded["board_id"],
        column_id=seeded["todo_id"],
    )

    assert result.id == seeded["todo_id"]
    assert result.label == "To Do"


def test_delete_column_success():
    seeded = _seed_board()

    result = delete_column(
        seeded["actor"],
        board_id=seeded["board_id"],
        column_id=seeded["todo_id"],
    )

    assert result is True
