from typing import List, Optional
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.board import Board
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse
from app.db.database import get_db_session
from sqlalchemy import func
from utils.exceptions import NotFoundException, APIException
def get_tasks(
    board_id: int,
    user_id: Optional[str] = None,
    assigned_to: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    limit: int = 50,
    offest: int = 0,
) -> List[TaskResponse]:
    with get_db_session() as db:

        query = db.query(Task)

        if board_id:
            check_board = db.query(Board).filter(Board.id == board_id).first()
            if not check_board:
                raise NotFoundException(message=f"Board with ID {board_id} not found!")
            query = query.filter(Task.board_id == board_id)

        if user_id:
            query = query.filter(Task.user_id == user_id)
        if assigned_to:
            query = query.filter(Task.assigned_to == assigned_to)
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)

        data = query.order_by(Task.created_at.desc()).limit(limit).offset(offest).all()

        return [TaskResponse.model_validate(task) for task in data]


def get_task_by_id(task_id: int) -> Optional[TaskResponse]:
    with get_db_session() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            return TaskResponse.model_validate(task)
        raise NotFoundException(message=f"Task with ID {task_id} not found!")


def get_user_tasks(user_id: int):
    with get_db_session() as db:
        data = (
            db.query(Task)
            .filter(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
            .all()
        )

        return [TaskResponse.model_validate(task) for task in data]


def create_task(task_data: TaskCreate) -> TaskResponse:
    with get_db_session() as db:
        db_task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            user_id=task_data.user_id,
            assigned_to=task_data.assigned_to,
            board_id=task_data.board_id,
            due_date=task_data.due_date,
        )

        db.add(db_task)
        db.flush()
        db.refresh(db_task)

        return TaskResponse.model_validate(db_task)


def update_task(task_id: int, task_data: TaskUpdate) -> Optional[TaskResponse]:
    with get_db_session() as db:
        db_task = db.query(Task).filter(Task.id == task_id).first()

        if not db_task:
            raise NotFoundException(message=f"Task with ID {task_id} not found!")

        for field, value in task_data.model_dump(exclude_unset=True).items():
            setattr(db_task, field, value)

        db_task.updated_at = func.now()
        db.flush()
        db.refresh(db_task)

        return TaskResponse.model_validate(db_task)


def delete_task(task_id: int) -> bool:
    with get_db_session() as db:
        db_task = db.query(Task).filter(Task.id == task_id).first()

        if not db_task:
            raise NotFoundException(message=f"Task with ID {task_id} not found!")

        db.delete(db_task)
        db.flush()
        return True


def get_task_stats() -> dict:
    with get_db_session() as db:
        db_rows = db.query(Task.status, Task.priority, Task.user_id).all()

        tasks_by_status = {s.value: 0 for s in TaskStatus}
        tasks_by_priority = {p.value: 0 for p in TaskPriority}
        tasks_by_user = {}
        for status, priority, user_id in db_rows:
            tasks_by_status[status.value] += 1
            tasks_by_priority[priority.value] += 1
            tasks_by_user[user_id] = tasks_by_user.get(user_id, 0) + 1

        return {
            "total_tasks": len(db_rows),
            "tasks_by_status": tasks_by_status,
            "tasks_by_priority": tasks_by_priority,
            "tasks_by_user": tasks_by_user,
        }
