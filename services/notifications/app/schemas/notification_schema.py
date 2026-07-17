from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models import utc_now


class NotificationSchema(BaseModel):
    id: int = Field(...)
    user_id: str = Field(...)
    type: str = Field(...)
    subject: Optional[str] = Field(None)
    body: str = Field(...)
    is_read: bool = Field(..., default_factory=False)
    created_at: datetime = Field(..., default_factory=utc_now)

    model_config = ConfigDict(from_attributes=True)


class NotificationCreateSchema(BaseModel):
    user_id: str = Field(...)
    type: str = Field(...)
    subject: Optional[str] = Field(None)
    body: str = Field(...)
    is_read: bool = Field(...)

    model_config = ConfigDict(from_attributes=True)


class NotificationUpdateSchema(BaseModel):
    type: Optional[str] = Field(None)
    subject: Optional[str] = Field(None)
    body: Optional[str] = Field(None)
    is_read: Optional[bool] = Field(None)
