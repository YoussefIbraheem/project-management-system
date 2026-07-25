from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from . import Base, datetime, utc_now
from .email_log import EmailLog

if TYPE_CHECKING:
    from .email_log import EmailLog
    from .user_replica import UserReplica


class Notification(Base,table=True):

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True,foreign_key="userreplica.user_id")
    type: str = Field(index=True)
    subject: Optional[str] = None
    body: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now)

    user_replica: "UserReplica" = Relationship(back_populates="notifications")
    email_logs: list["EmailLog"] = Relationship(back_populates="notification")