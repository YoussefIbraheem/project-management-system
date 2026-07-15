from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class NotificationSchema(BaseModel):
    id: str
    user_id: str
    type: str
    subject: Optional[str]
    title: str
    body: str
    is_read: bool
    created_at: datetime


class NotificationCreateSchema(BaseModel):
    user_id: str = Field(...)
    type: str = Field(...)
    subject: Optional[str] = Field(None)
    title: str = Field(...)
    body: str = Field(...)
    is_read: bool = Field(...)


class NotificationUpdateSchema(BaseModel):
    type: Optional[str] = Field(None)
    subject: Optional[str] = Field(None)
    title: Optional[str] = Field(None)
    body: Optional[str] = Field(None)
    is_read: Optional[bool] = Field(None)
