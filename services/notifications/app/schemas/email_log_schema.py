from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.email_log import EmailStatus


class EmailLogSchema(BaseModel):
    id: int = Field(...)
    email_address: str = Field(...)
    notification_id: int = Field(...)
    recipient_email: str = Field(...)
    status: str = EmailStatus.PENDING.value
    attempts: int = 0
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
