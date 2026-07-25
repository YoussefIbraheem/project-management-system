from datetime import datetime, timezone

from sqlmodel import SQLModel


def utc_now():
    return datetime.now(timezone.utc) 

class Base(SQLModel):
    pass

# # Added for Alembic auto generation to recognize the base class for models
# from .user_replica import UserReplica
# from .notification import Notification
# from .email_log import EmailLog