from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from utils.publisher import publish_history_event
from app.events.board_event import BoardCreatedEvent

from .. import logger
from . import Base


class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    columns = Column(
        JSON, nullable=True, default=lambda: ["ToDO", "InProgress", "Done"]
    )

    project_id = Column(Integer, ForeignKey("projects.id"), index=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="boards")
    tasks = relationship("Task", back_populates="board", cascade="all, delete-orphan")
