from dataclasses import dataclass
from typing import Optional
from . import BaseEvent


class TaskCreatedEvent(BaseEvent):
    def __init__(
        self,
        actor_id: str,
        subject_id: str,
        board_id: str,
        title: str,
        description: Optional[str] = None,
        status: Optional[str] = "To Do",
    ):
        self.metadata = {
            "title": title,
            "description": description,
            "board_id": board_id,
            "status": status,
        }
        super().__init__(
            metadata=self.metadata, actor_id=actor_id, subject_id=subject_id, subject_type="task"
        )

class TaskUpdatedEvent(BaseEvent):
    def __init__(
        self,
        actor_id: str,
        subject_id: str,
        board_id: str,
        updated_fields: Optional[list] = [],
    ):
        self.metadata = {
            "board_id": board_id,
            "updated_fields": updated_fields,
        }
        super().__init__(
            metadata=self.metadata, actor_id=actor_id, subject_id=subject_id, subject_type="task"
        )
        

class TaskDeletedEvent(BaseEvent):
    def __init__(
        self,
        actor_id: str,
        subject_id: str,
    ):
        super().__init__(actor_id=actor_id, subject_id=subject_id, subject_type="task")