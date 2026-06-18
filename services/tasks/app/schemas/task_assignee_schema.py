from pydantic import BaseModel, Field
from datetime import datetime

class TaskAssigneeBase(BaseModel):
    task_id: int
    user_id: str

class TaskAssigneeCreate(TaskAssigneeBase):
    pass
