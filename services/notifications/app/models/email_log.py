from sqlmodel import Field, Relationship
from . import datetime , utc_now , Base
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .notification import Notification

class EmailStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"

class EmailLog(Base,table=True):
     
    id: int | None = Field(default=None, primary_key=True)
    email_address: str = Field(index=True)
    notification_id: int = Field(foreign_key="notification.id")
    recipient_email: str
    status: str = Field(default=EmailStatus.PENDING.value)
    attempts: int = 0
    error_message: str | None = None
    sent_at: datetime = Field(default_factory=utc_now)

    notification: "Notification" = Relationship(back_populates="email_logs")