from datetime import datetime, timezone
from typing import Any, Dict

from beanie import Document
from pydantic import BeforeValidator, Field
from typing_extensions import Annotated

DateTimeUTC = Annotated[
    datetime,
    BeforeValidator(
        lambda v: (
            v.replace(tzinfo=timezone.utc)
            if isinstance(v, datetime) and v.tzinfo is None
            else v
        )
    ),
]

def utc_now():
    return datetime.now(timezone.utc)    


class Event(Document):
    actor_id: str
    service: str
    action: str
    subject_id: str
    subject_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    timestamp: DateTimeUTC = Field(default_factory=utc_now)

    class Settings:
        name = "events"
