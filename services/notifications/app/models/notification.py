from sqlmodel import Field, Relationship
from . import datetime , utc_now , Base
from typing import Optional
from enum import StrEnum
from .email_log import EmailLog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_replica import UserReplica
    from .email_log import EmailLog


class NotificationType(StrEnum):
    PROJECT_MEMBER_ADDED = "project_member_added"
    PROJECT_MEMBER_REMOVED = "project_member_removed"

    TASK_ASSIGNED = "task_assigned"
    TASK_UNASSIGNED = "task_unassigned"

    TASK_UPDATED = "task_updated"

    TASK_DUE_SOON = "task_due_soon"

class Notification(Base,table=True):

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True,foreign_key="userreplica.user_id")
    type: str = Field(index=True)
    subject: Optional[str] = None
    title: str
    body: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now)

    user_replica: "UserReplica" = Relationship(back_populates="notifications")
    email_logs: list["EmailLog"] = Relationship(back_populates="notification")