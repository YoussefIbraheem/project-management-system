from datetime import datetime, timezone
from typing import List, Optional

from shared.event import Event, EventAction, SubjectType
from shared.publishers import publish_history_event, publish_notification_event
from sqlalchemy import select
from sqlalchemy.orm import load_only

from app.db.database import get_db_session
from app.models import Board, Task
from app.models.project_member import ProjectMember
from app.models.task_assignee import TaskAssignee
from app.permissions.task_permission import (
    can_create_task,
    can_create_task_assignee,
    can_delete_task,
    can_delete_task_assignee,
    can_update_task,
    can_view_task,
    can_view_tasks,
)
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate
from app.security.actor import Actor
from app.validators.board_validator import (
    get_board_or_404,
    get_column_or_404,
)
from app.validators.project_validator import get_project_or_404
from app.validators.task_validator import (
    get_task_assignees_by_ids,
    get_task_or_404,
    normalize_assignee_ids,
    validate_project_membership,
    validate_task_assignment_state,
    validate_task_unassignment_state,
)


def get_tasks(
    actor: Actor,
    project_id: int,
    board_id: Optional[int] = None,
    creator_id: Optional[str] = None,
    assigned_to: Optional[str] = None,
    column_id: Optional[int] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[TaskResponse]:
    with get_db_session() as db:
        get_project_or_404(db, project_id)
        can_view_tasks(db, actor, project_id)

        query = db.query(Task).join(Board).filter(Board.project_id == project_id)

        if board_id:
            query = query.filter(Task.board_id == board_id)
        if creator_id:
            query = query.filter(Task.creator_id == creator_id)
        if assigned_to:
            query = query.filter(Task.assignees.any(user_id=assigned_to))
        if column_id:
            query = query.filter(Task.column_id == column_id)
        if priority:
            query = query.filter(Task.priority == priority)

        data = query.order_by(Task.created_at.desc()).limit(limit).offset(offset).all()
        return [TaskResponse.model_validate(task) for task in data]


def get_task_by_id(actor: Actor, task_id: int) -> TaskResponse:
    with get_db_session() as db:
        task = get_task_or_404(db, task_id)
        project = task.board.project
        can_view_task(db, actor, project.id)
        return TaskResponse.model_validate(task)


def get_user_tasks(actor: Actor):
    with get_db_session() as db:
        data = (
            db.query(Task)
            .filter(Task.creator_id == actor.user_id)
            .order_by(Task.created_at.desc())
            .all()
        )

        return [TaskResponse.model_validate(task) for task in data]


def create_task(actor: Actor, task_data: TaskCreate) -> TaskResponse:
    with get_db_session() as db:
        board = get_board_or_404(db, task_data.board_id)
        column = get_column_or_404(db, board.id, task_data.column_id)
        project_members_ids_stmt = (
            select(ProjectMember)
            .options(load_only(ProjectMember.user_id))
            .where(ProjectMember.project_id == board.project_id)
        )
        project_members_ids = [
            project_member.user_id
            for project_member in db.execute(project_members_ids_stmt).scalars()
        ]
        can_create_task(db, actor, board.project_id)
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

        event = Event(
            actor_id=actor.user_id,
            subject_id=str(db_task.id),
            subject_type=SubjectType.TASK,
            action=EventAction.TASK_CREATE,
            metadata={
                "task_title": db_task.title,
                "project_name": board.project.name,
                "task_title": db_task.title,
                "recipients_ids": project_members_ids,
            },
        )

        publish_notification_event(event)
        publish_history_event(event)

        return TaskResponse.model_validate(db_task)


def update_task(actor: Actor, task_id: int, task_data: TaskUpdate) -> TaskResponse:
    with get_db_session() as db:
        db_task = get_task_or_404(db, task_id)
        project = db_task.board.project
        can_update_task(db, actor, project.id)
        updated_fields = []
        for field, value in task_data.model_dump(exclude_unset=True).items():
            setattr(db_task, field, value)
            updated_fields.append({field: value})

        db_task.updated_at = datetime.now(timezone.utc)
        assignees_ids_stmt = (
            select(TaskAssignee)
            .options(load_only(TaskAssignee.user_id))
            .where(TaskAssignee.task_id == task_id)
        )
        assignees_ids = [
            assignee_id for assignee_id in db.execute(assignees_ids_stmt).scalars()
        ]
        db.flush()
        db.refresh(db_task)
        event = Event(
            actor_id=actor.user_id,
            subject_id=str(db_task.id),
            subject_type=SubjectType.TASK,
            action=EventAction.TASK_UPDATE,
            metadata={
                "updated_fields": updated_fields,
                "recipients_ids": assignees_ids,
                "project_name": project.name,
                "task_title": db_task.title,
            },
        )

        publish_notification_event(event)
        publish_history_event(event)

        return TaskResponse.model_validate(db_task)


def delete_task(actor: Actor, task_id: int) -> bool:
    with get_db_session() as db:
        db_task = get_task_or_404(db, task_id)
        project = db_task.board.project

        can_delete_task(db, actor, project.id, db_task)

        db.delete(db_task)
        db.flush()

    event = Event(
        actor_id=actor.user_id,
        subject_id=str(db_task.id),
        subject_type=SubjectType.TASK,
        action=EventAction.TASK_DELETE,
    )
    publish_notification_event(event)
    publish_history_event(event)

    return True


def assign_task(actor: Actor, task_id: int, assignees_ids: list[str]) -> TaskResponse:
    with get_db_session() as db:
        task = get_task_or_404(db, task_id)
        project = task.board.project

        normalized_assignees_ids = normalize_assignee_ids(assignees_ids)

        for assignee_id in normalized_assignees_ids:
            can_create_task_assignee(db, actor, project.id, task, assignee_id)

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

        event = Event(
            actor_id=actor.user_id,
            subject_id=str(task_id),
            subject_type=SubjectType.TASK,
            action=EventAction.TASK_ASSIGN,
            metadata={
                "recipients_ids": normalized_assignees_ids,
                "project_name": project.name,
                "task_title": task.title,
            },
        )

        publish_notification_event(event)
        publish_history_event(event)

        return TaskResponse.model_validate(task)


def unassign_task(actor: Actor, task_id: int, assignees_ids: list[str]) -> TaskResponse:
    with get_db_session() as db:
        task = get_task_or_404(db, task_id)
        project = task.board.project
        normalized_assignees_ids = normalize_assignee_ids(assignees_ids)
        for assignee_id in normalized_assignees_ids:
            can_delete_task_assignee(db, actor, project.id, task, assignee_id)

        validate_task_unassignment_state(db, task, normalized_assignees_ids)

        for assignee in get_task_assignees_by_ids(db, task, normalized_assignees_ids):
            db.delete(assignee)

        db.flush()
        db.refresh(task)
        event = Event(
            actor_id=actor.user_id,
            subject_id=str(task_id),
            subject_type=SubjectType.TASK,
            action=EventAction.TASK_UNASSIGN,
            metadata={
                "recipients_ids": normalized_assignees_ids,
                "task_title": task.title,
                "project_name": project.name,
            },
        )

        publish_notification_event(event)
        publish_history_event(event)

        return TaskResponse.model_validate(task)


# def get_task_stats() -> dict:
#     with get_db_session() as db:
#         db_rows = db.query(Task.priority, Task.creator_id).all()

#         tasks_by_priority = {p: 0 for p in TaskPriority}
#         tasks_by_creator = {}
#         for priority, creator_id in db_rows:
#             tasks_by_priority[priority] += 1
#             tasks_by_creator[creator_id] = tasks_by_creator.get(creator_id, 0) + 1

#         return {
#             "total_tasks": len(db_rows),
#             "tasks_by_priority": tasks_by_priority,
#             "tasks_by_user": tasks_by_creator,
#         }
