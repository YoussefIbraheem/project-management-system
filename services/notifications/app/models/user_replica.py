from sqlmodel import Field, Relationship
from . import datetime , utc_now , Base
from typing import TYPE_CHECKING
from .notification import Notification

class UserReplica(Base, table=True):
    __tablename__ = "user_replicas" #type: ignore
    
    user_id: str = Field(primary_key=True, index=True)
    email: str = Field(index=True)
    display_name: str | None = None
    
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime | None = Field(default=None)
    
    notifications:list["Notification"] = Relationship(back_populates="user_replica")
    
