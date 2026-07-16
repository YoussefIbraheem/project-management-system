from datetime import datetime, timezone

import pytest
from app import logger
from app.db.database import get_db_session
from app.models import Board, BoardColumn, Project, ProjectMember, Task
from app.models.task import TaskPriority
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.security.actor import Actor
from app.security.roles import MemberRole
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
        actor = Actor(user_id="1", is_superuser=True)
        db.add(project)
        db.flush()
        
        members = []
        for i in range(1,5):
            members.append(
                ProjectMember(
                    project_id=project.id,
                    user_id=str(i),
                    role=MemberRole.MANAGER.db_value,
                )
            )
        db.add_all(members)
        db.flush()
        
        board = Board(name="Board 1", description="Main board", project_id=project.id)
        db.add(board)
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
            creator_id="1",
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
            "actor": actor,
            "members_ids":[member.user_id for member in members]
        }


def test_get_tasks_returns_tasks():
    seeded = _seed_task()

    tasks = get_tasks(
        actor=seeded["actor"],
        project_id=seeded["project_id"],
        board_id=seeded["board_id"],
        limit=10,
        offset=0,
    )

    assert len(tasks) >= 1
    assert tasks[0].board_id == seeded["board_id"]


def test_get_task_by_id_returns_task():
    seeded = _seed_task()

    task = get_task_by_id(seeded["actor"], seeded["task_id"])

    assert task.id == seeded["task_id"]
    assert task.title == "Task 1"


def test_create_task_persists_task():
    seeded = _seed_task()

    task = create_task(
        seeded["actor"],
        TaskCreate(
            title="Created Task",
            description="Body",
            column_id=seeded["doing_id"],
            priority=TaskPriority.MEDIUM.db_value,
            creator_id="user-1",
            board_id=seeded["board_id"],
            due_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        ),
    )

    assert task.title == "Created Task"
    assert task.creator_id == "user-1"


def test_update_task_updates_fields():
    seeded = _seed_task()

    task = update_task(
        seeded["actor"],
        seeded["task_id"],
        TaskUpdate(title="Updated Task", priority=TaskPriority.HIGH.db_value), #type: ignore
    )

    logger.info(f"UPDATED TASK DATA:{task}")

    assert task.title == "Updated Task"
    assert task.priority == TaskPriority.HIGH.db_value


def test_assign_and_unassign_task():
    seeded = _seed_task()
    members_ids = seeded["members_ids"]
    assigned = assign_task(seeded["actor"], seeded["task_id"], members_ids)
    assert len(assigned.assignees) == len(members_ids)

    unassigned = unassign_task(seeded["actor"], seeded["task_id"], members_ids)
    assert unassigned.assignees == []

def test_delete_task_returns_true():
    seeded = _seed_task()

    assert delete_task(seeded["actor"], seeded["task_id"]) is True


def test_get_task_by_id_raises_not_found():
    seeded = _seed_task()
    with pytest.raises(NotFoundException):
        get_task_by_id(seeded["actor"], 999)
