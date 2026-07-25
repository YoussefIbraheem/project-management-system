from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum

from app.core.flask_enum import FlaskEnum


class SubjectType(FlaskEnum):
    PROJECT = "PROJECT", "Project"
    BOARD = "BOARD", "Board"
    TASK = "TASK", "Task"


class EventAction(StrEnum):
    PROJECT_CREATE = "PROJECT_CREATE"
    PROJECT_UPDATE = "PROJECT_UPDATE"
    PROJECT_DELETE = "PROJECT_DELETE"
    PROJECT_MEMBER_ADD = "PROJECT_MEMBER_ADD"
    PROJECT_MEMBER_UPDATE = "PROJECT_MEMBER_UPDATE"
    PROJECT_MEMBER_DELETE = "PROJECT_MEMBER_DELETE"
    BOARD_CREATE = "BOARD_CREATE"
    BOARD_UPDATE = "BOARD_UPDATE"
    BOARD_DELETE = "BOARD_DELETE"
    BOARD_COLUMN_CREATE = "BOARD_COLUMN_CREATE"
    BOARD_COLUMN_DELETE = "BOARD_COLUMN_DELETE"
    TASK_CREATE = "TASK_CREATE"
    TASK_UPDATE = "TASK_UPDATE"
    TASK_DELETE = "TASK_DELETE"
    TASK_ASSIGN = "TASK_ASSIGN"
    TASK_UNASSIGN = "TASK_UNASSIGN"


@dataclass
class Event:
    actor_id: str
    subject_id: str
    subject_type: SubjectType
    action: EventAction
    service: str = "tasks"
    metadata: dict = field(default_factory=dict)
    # NOTE: timestamp gets generated automatically in the history service no need to send it to avoid confusion

    def __post_init__(self):
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        subject_type = self.subject_type.db_value
        action = self.action.value
        data = asdict(self)
        data["subject_type"] = (
            subject_type  # NOTE: This is used to conver the SubjectType into its string form
        )
        data["action"] = (
            action  # NOTE: This is used to conver the SubjectType into its string form
        )
        return data
