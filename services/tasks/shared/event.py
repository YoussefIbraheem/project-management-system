from dataclasses import asdict, dataclass, field
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
    metadata: dict = field(default_factory=dict)
    # NOTE: timestamp gets generated automatically in the history service no need to send it to avoid confusion

    def __post_init__(self):
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        subject_type = self.subject_type.db_value
        data = asdict(self)
        data["subject_type"] = subject_type # NOTE: This is used to conver the SubjectType into its string form
        return data
