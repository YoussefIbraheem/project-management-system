from datetime import datetime, timezone

import pytest
from app.db.database import get_db_session
from app.models import Board, BoardColumn, Project, ProjectMember, Task
from app.security.roles import MemberRole
from app.models.task import TaskPriority
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.services.task_service import (
    assign_task,
    create_task,
    delete_task,
    get_task_by_id,
    get_tasks,
    unassign_task,
    update_task,
)
from shared.exceptions import NotFoundException


def _seed_task():
    with get_db_session() as db:
        project = Project(name="Alpha", description="Project Alpha")
        db.add(project)
        db.flush()

        member = ProjectMember(
            project_id=project.id, user_id="user-1", role=MemberRole.MANAGER.db_value
        )
        board = Board(name="Board 1", description="Main board", project_id=project.id)
        db.add_all([member, board])
        db.flush()

        todo = BoardColumn(
            board_id=board.id, slug="todo", label="To Do", status_group="pending"
        )
        doing = BoardColumn(
            board_id=board.id, slug="doing", label="Doing", status_group="in_progress"
        )
        db.add_all([todo, doing])
        db.flush()

        task = Task(
            title="Task 1",
            description="Task description",
            column_id=todo.id,
            priority=TaskPriority.LOW.db_value,
            due_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
            creator_id="user-1",
            board_id=board.id,
        )
        db.add(task)
        db.flush()
        db.refresh(task)
        return {
            "project_id": project.id,
            "board_id": board.id,
            "todo_id": todo.id,
            "doing_id": doing.id,
            "task_id": task.id,
        }


def test_get_tasks_returns_tasks():
    seeded = _seed_task()

    tasks = get_tasks(board_id=seeded["board_id"], limit=10, offest=0) #type: ignore

    assert len(tasks) >= 1
    assert tasks[0].board_id == seeded["board_id"]


def test_get_task_by_id_returns_task():
    seeded = _seed_task()

    task = get_task_by_id(seeded["task_id"]) #type: ignore

    assert task.id == seeded["task_id"] #type: ignore
    assert task.title == "Task 1" #type: ignore


def test_create_task_persists_task():
    seeded = _seed_task()

    task = create_task(
        TaskCreate(
            title="Created Task",
            description="Body",
            column_id=seeded["doing_id"], #type: ignore
            priority=TaskPriority.MEDIUM.db_value,
            creator_id="user-1",
            board_id=seeded["board_id"], #type: ignore
            due_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        )
    )

    assert task.title == "Created Task"
    assert task.creator_id == "user-1"


def test_update_task_updates_fields():
    seeded = _seed_task()

    task = update_task(
        seeded["task_id"], #type: ignore
        TaskUpdate(title="Updated Task", priority=TaskPriority.HIGH.db_value), #type: ignore
    )

    assert task.title == "Updated Task"
    assert task.priority == TaskPriority.HIGH.db_value


def test_assign_and_unassign_task():
    seeded = _seed_task()

    assigned = assign_task(seeded["task_id"], ["user-1"])  #type: ignore
    assert len(assigned.assignees) == 1

    unassigned = unassign_task(seeded["task_id"], ["user-1"]) #type: ignore
    assert unassigned.assignees == []


def test_delete_task_returns_true():
    seeded = _seed_task()

    assert delete_task(seeded["task_id"]) is True #type: ignore


def test_get_task_by_id_raises_not_found():
    with pytest.raises(NotFoundException):
        get_task_by_id(999)
