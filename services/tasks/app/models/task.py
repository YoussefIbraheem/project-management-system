from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as FlaskEnum
from . import Base

class TaskPriority(FlaskEnum):
    """
    Enum for task priority.
    LOW: Low priority.
    MEDIUM: Medium priority.
    HIGH: High priority.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(Base):

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    column_id = Column(Integer,ForeignKey("board_columns.id"),nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = Column(DateTime(timezone=True),nullable=False)
    owner_id = Column(String(255), nullable=False, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    board = relationship("Board",back_populates="tasks")
    column = relationship("BoardColumn",back_populates="tasks")
