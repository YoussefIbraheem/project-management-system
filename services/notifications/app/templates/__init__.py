from dataclasses import dataclass
from typing import Optional



@dataclass
class NotificationContent:
    subject: str
    body: str
    recipient_email:str

@dataclass
class NotificationContext:
    recipient_email:str
    username: str
    actor_username: str
    task_title: Optional[str]
    project_name: str | None
    
