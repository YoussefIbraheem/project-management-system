from datetime import datetime, timezone
from typing import Annotated, Any, ClassVar

import pymongo
from beanie import Document
from pydantic import BeforeValidator, Field

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
    metadata: dict[str, Any] = Field(default_factory=dict)

    timestamp: DateTimeUTC = Field(default_factory=utc_now)

    class Settings:
        name = "events"
        indexes: ClassVar = [
            [
                ("service", pymongo.ASCENDING),
                ("actor_id", pymongo.ASCENDING),
                ("timestamp", pymongo.DESCENDING),
            ],
            [("actor_id", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)],
            [("timestamp", pymongo.DESCENDING)],
        ]
