from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field

from app.models import TaskPriority


class TaskAssignee(BaseModel):
    user_id: str

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    id: int = Field(..., description="Task ID")
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Description")
    priority: str = TaskPriority.LOW.db_value
    column_id: int = Field(..., description="ID of the parent column")
    creator_id: str = Field(..., description="ID of the task creator")
    board_id: int = Field(..., description="ID of the parent board")
    due_date: datetime | None = Field(None, description="Due date of the task")
    assignees: list[TaskAssignee] = Field([], description="List of assignees")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime | None = Field(None, description="Task update timestamp")

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class TaskResponse(TaskBase):
    pass


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Description")
    column_id: int = Field(..., description="ID of the parent column")
    priority: str = TaskPriority.LOW.db_value
    creator_id: str = Field(..., description="Creator ID")
    board_id: int = Field(..., description="ID of the parent board")
    due_date: datetime | None = datetime.now(timezone.utc)


class TaskUpdate(BaseModel):
    title: str | None = Field(
        None, min_length=1, max_length=255, description="Task title"
    )
    description: str | None = Field(None, max_length=1000, description="Description")
    priority: str | None = Field(None, description="Task priority")
    column_id: int | None = Field(None, description="ID of the parent column")
    due_date: datetime | None = Field(None, description="Due date of the task")

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class TaskStats(BaseModel):
    total_tasks: int = Field(..., description="Total number of tasks")
    tasks_by_status: dict = Field(..., description="Number of tasks by status")
    tasks_by_priority: dict = Field(..., description="Number of tasks by priority")


class TaskAssign(BaseModel):
    assignees_ids: list[str] = Field(..., description="List of assignee IDs")


class TaskUnassign(BaseModel):
    assignees_ids: list[str] = Field(..., description="List of unassignee IDs")
