from collections.abc import Iterable

from utils.exceptions import ConflictException, NotFoundException, ValidationException

from app.models import Board, BoardColumn, Task
from app.models.project_member import ProjectMember
from app.models.task_assignee import TaskAssignee


def get_task_or_404(db, task_id: int) -> Task:
    """
    Retrieve a task by its ID or raise a 404 error if not found.
    - db: SQLAlchemy database session
    - task_id: ID of the task to retrieve
    - return: The retrieved task object
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise NotFoundException(message=f"Task with ID {task_id} not found!")
    return task


def normalize_assignee_ids(assignees_ids: list[str]) -> list[str]:
    """
    Normalize and validate a list of assignee IDs.
    - assignees_ids: List of assignee IDs as strings
    - return: Normalized list of assignee IDs
    """
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
    """
    Validate that all assignee IDs belong to the same project as the task.

    - db: Database session.
    - task: The task to validate.
    - assignees_ids: List of assignee IDs to validate.

    """    
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
    """
    Validate that the task has at least one assignee before unassigning.
    - db: Database session.
    - task: Task object.
    - assignees_ids: List of assignee IDs to unassign.
    """
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

def get_task_assignees_by_ids(db, task: Task, assignees_ids: list[str]) -> list[TaskAssignee]:
    """
    Retrieve a list of TaskAssignee objects for the given task and assignee IDs.
    
    - db: Database session.
    - task: Task object.
    - assignee_ids: List of assignee IDs to retrieve.
    - return: List of TaskAssignee objects.
    """
    return (
        db.query(TaskAssignee)
        .filter(
            TaskAssignee.task_id == task.id,
            TaskAssignee.user_id.in_(assignees_ids),
        )
        .all()
    )