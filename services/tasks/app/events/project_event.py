from typing import Optional
from app.events.base_event import BaseEvent, dataclass


@dataclass
class ProjectCreatedEvent(BaseEvent):
    def __init__(
        self,
        actor_id: str,
        subject_id: str,
        name: str,
        owner_id: str,
        description: Optional[dict] = None,
    ):
        self.metadata = {
            "name": name,
            "description": description,
            "owner_id": owner_id,
        }
        super().__init__(
            metadata=self.metadata,
            subject_id=subject_id,
            subject_type="project",
            actor_id=actor_id,
        )

@dataclass
class ProjectUpdatedEvent(BaseEvent):
    def __init__(
        self,
        actor_id: str,
        subject_id: str,
        owner_id: str,
        updated_fields: Optional[list] = [],
    ):

        self.metadata = {"updated_fields": updated_fields, "owner_id": owner_id}
        super().__init__(
            metadata=self.metadata,
            subject_id=subject_id,
            subject_type="project",
            actor_id=actor_id,
        )

@dataclass
class ProjectDeletedEvent(BaseEvent):
    def __init__(
        self,
        name: str,
        actor_id: str,
        subject_id: str,
        owner_id: str,
    ):
        self.metadata = {
            "name": name,
            "owner_id": owner_id,
        }
        super().__init__(
            metadata=self.metadata,
            subject_id=subject_id,
            subject_type="project",
            actor_id=actor_id,
        )
