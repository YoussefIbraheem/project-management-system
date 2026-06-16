from typing import Optional
from app.events.base_event import BaseEvent, dataclass


@dataclass
class BoardCreatedEvent(BaseEvent):
    def __init__(
        self,
        actor_id: str,
        subject_id: str,
        project_id: str,
        name:str,
        description: Optional[str] = None,
        columns: Optional[list] = [],
    ):
        self.metadata = {
            "name":name,
            "description": description,
            "project_id": project_id,
            "columns": columns,
        }
        super().__init__(metadata=self.metadata, actor_id=actor_id, subject_id=subject_id, subject_type="board")
        

@dataclass
class BoardUpdatedEvent(BaseEvent):
    def __init__(
        self,
        actor_id: str,
        subject_id: str,
        project_id: str,
        updated_fields: Optional[list] = [],
    ):
        self.metadata = {
            "project_id": project_id,
            "updated_fields": updated_fields,
        }
        super().__init__(metadata=self.metadata, actor_id=actor_id, subject_id=subject_id, subject_type="board")
        

@dataclass
class BoardDeletedEvent(BaseEvent):
    def __init__(
        self,
        actor_id: str,
        subject_id: str,
    ):
        super().__init__(actor_id=actor_id, subject_id=subject_id, subject_type="board")

