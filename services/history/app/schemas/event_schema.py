from datetime import datetime

from bson import ObjectId as _ObjectId
from app.models.event import DateTimeUTC, utc_now
from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

ObjectId = Annotated[
    str, BeforeValidator(lambda v: str(v) if isinstance(v, _ObjectId) else v)
]


class EventCreate(BaseModel):
    actor_id: str = Field(...)
    service: str = Field(...)
    action: str = Field(...)
    subject_id: str = Field(...)
    subject_type: str = Field(...)
    metadata: dict = Field(...)


class EventResponse(BaseModel):
    id: ObjectId = Field(..., alias="_id")
    actor_id: str = Field(...)
    service: str = Field(...)
    action: str = Field(...)
    subject_id: str = Field(...)
    subject_type: str = Field(...)
    metadata: dict = Field(...)
    timestamp: DateTimeUTC = Field(default_factory=utc_now)


class EventsStats(BaseModel):
    pass
