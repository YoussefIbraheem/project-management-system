from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models import utc_now #type: ignore


class NotificationSchema(BaseModel):
    id: int = Field(...)
    user_id: str = Field(...)
    type: str = Field(...)
    subject: Optional[str] = Field(None)
    body: str = Field(...)
    is_read: bool = False
    created_at: datetime = utc_now

    model_config = ConfigDict(from_attributes=True)
