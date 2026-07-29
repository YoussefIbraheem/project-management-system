from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import utc_now
from app.models.email_log import EmailStatus


class EmailLogSchema(BaseModel):
    id: int = Field(...)
    email_address: str = Field(...)
    notification_id: int = Field(...)
    recipient_email: str = Field(...)
    status: str = EmailStatus.PENDING.value
    attempts: int = 0
    error_message: str | None = None
    sent_at: datetime | None = None

    created_at: datetime = utc_now

    model_config = ConfigDict(from_attributes=True)
