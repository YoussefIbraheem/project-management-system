from pydantic import BaseModel, Field
from datetime import datetime


class TaskAssigneeBase(BaseModel):
    task: str = Field(..., description="Name of the task to assign")
    user: str = Field(..., description="Name of the user to assign the task")
    created_at: datetime = Field(..., description="Date and time when the task was assigned")


class TaskAssigneeResponse(TaskAssigneeBase):
    pass
 
class TaskAssigneeCreate(BaseModel):
    task_id: int = Field(...)
    user_id: str = Field(...)
    
