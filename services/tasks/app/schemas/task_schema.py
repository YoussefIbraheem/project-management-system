from datetime import datetime , timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority


class TaskBase(BaseModel):
    id: int = Field(..., description="Task ID")
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Description")
    column_id: int = Field(..., description="ID of the parent column")
    priority: TaskPriority = TaskPriority.LOW.db_value
    creator_id: str = Field(..., description="ID of the task creator")
    board_id: int = Field(..., description="ID of the parent board")
    assignees: Optional[list[str]] = Field([], description="List of assigned users")
    due_date: Optional[datetime] = Field(None, description="Due date of the task")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Task update timestamp")

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class TaskResponse(TaskBase):
    pass


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Description")
    column_id: int = Field(..., description="ID of the parent column")
    priority: str = TaskPriority.LOW.db_value
    creator_id: str = Field(..., description="Creator ID")
    assignees: list[str] = Field([], description="List of assigned users")
    board_id: int = Field(..., description="ID of the parent board")
    due_date: Optional[datetime] = datetime.now(timezone.utc)
    
    


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Task title"
    )
    description: Optional[str] = Field(None, max_length=1000, description="Description")
    priority: Optional[TaskPriority] = Field(None, description="Task priority")
    user_id: Optional[str] = Field(None, description="ID of the task owner")
    assignees: Optional[list] = Field([], description="ID of the task assingee")
    board_id: Optional[int] = Field(None, description="ID of the parent board")
    due_date: Optional[datetime] = Field(None, description="Due date of the task")

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class TaskStats(BaseModel):
    total_tasks: int = Field(..., description="Total number of tasks")
    tasks_by_status: dict = Field(..., description="Number of tasks by status")
    tasks_by_priority: dict = Field(..., description="Number of tasks by priority")
