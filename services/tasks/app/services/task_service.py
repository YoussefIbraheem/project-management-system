from datetime import datetime, timezone
from typing import List, Optional

from app.db.database import get_db_session
from app.models import Task
from app.models.task import TaskPriority
from app.models.task_assignee import TaskAssignee
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
from app.validators.board_validator import (
    get_board_or_404,
    get_column_or_404,
)
from app.validators.task_validator import (
    get_task_assignees_by_ids,
    get_task_or_404,
    normalize_assignee_ids,
    validate_project_membership,
    validate_task_assignment_state,
    validate_task_unassignment_state,
)


def get_tasks(
    board_id: int,
    creator_id: Optional[str] = None,
    assigned_to: Optional[str] = None,
    column_id: Optional[int] = None,
    priority: Optional[TaskPriority] = None,
    limit: int = 50,
    offest: int = 0,
) -> List[TaskResponse]:
    with get_db_session() as db:
        query = db.query(Task)

        if board_id:
            board = get_board_or_404(db, board_id)
            query = query.filter(Task.board_id == board.id)

        if creator_id:
            query = query.filter(Task.creator_id == creator_id)
        if assigned_to:
            query = query.filter(Task.assignees.any(user_id=assigned_to))
        if column_id:
            query = query.filter(Task.column_id == column_id)
        if priority:
            query = query.filter(Task.priority == priority)

        data = query.order_by(Task.created_at.desc()).limit(limit).offset(offest).all()
        return [TaskResponse.model_validate(task) for task in data]


def get_task_by_id(task_id: int) -> Optional[TaskResponse]:
    with get_db_session() as db:
        task = get_task_or_404(db, task_id)
        return TaskResponse.model_validate(task)


def get_user_tasks(user_id: int):
    with get_db_session() as db:
        data = (
            db.query(Task)
            .filter(Task.creator_id == user_id)
            .order_by(Task.created_at.desc())
            .all()
        )

        return [TaskResponse.model_validate(task) for task in data]


def create_task(task_data: TaskCreate) -> TaskResponse:
    with get_db_session() as db:
        board = get_board_or_404(db, task_data.board_id)
        column = get_column_or_404(db, board.id, task_data.column_id)  # type: ignore[assignment]

        db_task = Task(
            title=task_data.title,
            description=task_data.description,
            column_id=column.id,
            priority=task_data.priority,
            creator_id=task_data.creator_id,
            board_id=task_data.board_id,
            due_date=task_data.due_date,
        )

        db.add(db_task)
        db.flush()
        db.refresh(db_task)
        return TaskResponse.model_validate(db_task)


def update_task(task_id: int, task_data: TaskUpdate) -> TaskResponse:
    with get_db_session() as db:
        db_task = get_task_or_404(db, task_id)

        for field, value in task_data.model_dump(exclude_unset=True).items():
            setattr(db_task, field, value)

        db_task.updated_at = datetime.now(timezone.utc)  # type: ignore[assignment]
        db.flush()
        db.refresh(db_task)
        return TaskResponse.model_validate(db_task)


def delete_task(task_id: int) -> bool:
    with get_db_session() as db:
        db_task = get_task_or_404(db, task_id)
        db.delete(db_task)
        db.flush()
        return True


def assign_task(task_id: int, assignees_ids: list[str]) -> TaskResponse:
    with get_db_session() as db:
        task = get_task_or_404(db, task_id)
        normalized_assignees_ids = normalize_assignee_ids(assignees_ids)
        validate_project_membership(db, task, normalized_assignees_ids)
        validate_task_assignment_state(db, task, normalized_assignees_ids)

        db.add_all(
            [
                TaskAssignee(user_id=assignee_id, task_id=task.id)
                for assignee_id in normalized_assignees_ids
            ]
        )
        db.flush()
        db.refresh(task)
        return TaskResponse.model_validate(task)


def unassign_task(task_id: int, assignees_ids: list[str]) -> TaskResponse:
    with get_db_session() as db:
        task = get_task_or_404(db, task_id)
        normalized_assignees_ids = normalize_assignee_ids(assignees_ids)
        validate_task_unassignment_state(db, task, normalized_assignees_ids)

        for assignee in get_task_assignees_by_ids(db, task, normalized_assignees_ids):
            db.delete(assignee)

        db.flush()
        db.refresh(task)
        return TaskResponse.model_validate(task)


def get_task_stats() -> dict:
    with get_db_session() as db:
        db_rows = db.query(Task.priority, Task.creator_id).all()

        tasks_by_priority = {p.value: 0 for p in TaskPriority}
        tasks_by_creator = {}
        for priority, creator_id in db_rows:
            tasks_by_priority[priority.value] += 1
            tasks_by_creator[creator_id] = tasks_by_creator.get(creator_id, 0) + 1

        return {
            "total_tasks": len(db_rows),
            "tasks_by_priority": tasks_by_priority,
            "tasks_by_user": tasks_by_creator,
        }
