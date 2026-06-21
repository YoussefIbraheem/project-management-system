from collections.abc import Iterable

from utils.exceptions import ConflictException, NotFoundException, ValidationException

from app.models import Board, BoardColumn, Task
from app.models.project_member import ProjectMember
from app.models.task_assignee import TaskAssignee


def get_task_or_404(db, task_id: int) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise NotFoundException(message=f"Task with ID {task_id} not found!")
    return task


def ensure_board_exists(db, board_id: int) -> Board:
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise NotFoundException(message=f"Board with ID {board_id} not found!")
    return board


def ensure_column_exists(db, column_id: int) -> BoardColumn:
    column = db.query(BoardColumn).filter(BoardColumn.id == column_id).first()
    if not column:
        raise NotFoundException(message=f"Column with ID {column_id} not found!")
    return column


def normalize_assignee_ids(assignees_ids: list[str]) -> list[str]:
    if not assignees_ids:
        raise ValidationException(message="Assignees list cannot be empty.")

    normalized: list[str] = []
    seen: set[str] = set()
    for assignee_id in assignees_ids:
        if not isinstance(assignee_id, str):
            raise ValidationException(message="Assignee IDs must be strings.")

        cleaned_assignee_id = assignee_id.strip()
        if not cleaned_assignee_id:
            raise ValidationException(message="Assignee IDs cannot be empty.")

        if cleaned_assignee_id in seen:
            raise ValidationException(
                message="Duplicate assignee IDs are not allowed.",
                data={"duplicate_assignee_id": cleaned_assignee_id},
            )

        seen.add(cleaned_assignee_id)
        normalized.append(cleaned_assignee_id)

    return normalized


def validate_project_membership(db, task: Task, assignees_ids: list[str]) -> list[str]:
    project_member_ids = {
        user_id
        for (user_id,) in db.query(ProjectMember.user_id)
        .filter(
            ProjectMember.project_id == task.board.project_id,
            ProjectMember.user_id.in_(assignees_ids),
        )
        .all()
    }

    invalid_assignees = [
        assignee_id
        for assignee_id in assignees_ids
        if assignee_id not in project_member_ids
    ]
    if invalid_assignees:
        raise ValidationException(
            message="One or more assignees are not members of the task project.",
            data={"invalid_assignees": invalid_assignees},
        )

    return assignees_ids


def validate_task_assignment_state(db, task: Task, assignees_ids: list[str]) -> None:
    already_assigned_ids = {
        user_id
        for (user_id,) in db.query(TaskAssignee.user_id)
        .filter(
            TaskAssignee.task_id == task.id,
            TaskAssignee.user_id.in_(assignees_ids),
        )
        .all()
    }
    if already_assigned_ids:
        raise ConflictException(
            message="One or more assignees are already assigned to this task.",
            data={"already_assigned": sorted(already_assigned_ids)},
        )


def validate_task_unassignment_state(db, task: Task, assignees_ids: list[str]) -> None:
    assigned_ids = {
        user_id
        for (user_id,) in db.query(TaskAssignee.user_id)
        .filter(
            TaskAssignee.task_id == task.id,
            TaskAssignee.user_id.in_(assignees_ids),
        )
        .all()
    }

    missing_assignees = [
        assignee_id for assignee_id in assignees_ids if assignee_id not in assigned_ids
    ]
    if missing_assignees:
        raise ValidationException(
            message="One or more assignees are not assigned to this task.",
            data={"missing_assignees": missing_assignees},
        )


def get_assignments_for_task(db, task: Task) -> list[TaskAssignee]:
    return db.query(TaskAssignee).filter(TaskAssignee.task_id == task.id).all()


def get_task_assignees_by_ids(
    db,
    task: Task,
    assignees_ids: Iterable[str],
) -> list[TaskAssignee]:
    return (
        db.query(TaskAssignee)
        .filter(
            TaskAssignee.task_id == task.id,
            TaskAssignee.user_id.in_(list(assignees_ids)),
        )
        .all()
    )
