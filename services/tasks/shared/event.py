from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.core.flask_enum import FlaskEnum


class SubjectType(FlaskEnum):
    PROJECT = "PROJECT", "Project"
    BOARD = "BOARD", "Board"
    TASK = "TASK", "Task"


@dataclass
class Event:
    actor_id: str
    subject_id: str
    subject_type: SubjectType
    action: str
    service: str = "tasks"
    timestamp: str = field(init=False)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        self.timestamp = datetime.now(timezone.utc).isoformat()
