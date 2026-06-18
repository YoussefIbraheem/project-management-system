from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    def to_dict(self):
        """Convert object to dictionary."""
        # check if the value is datetime and make it iso to be serializable
        data = {}
        for col in self.__table__.columns:
            attr = getattr(self, col.name)
            if isinstance(attr, datetime):
                setattr(self, col.name, attr.isoformat())
            data[col.name] = attr
        return data


# Added for Alembic auto generation to recognize the base class for models
from .board import Board
from .board_column import BoardColumn
from .project import Project
from .project_member import ProjectMember
from .task import Task
from .task_assignee import TaskAssignee
from .member_role import MemberRole 