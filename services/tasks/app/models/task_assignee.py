from . import Base, Column, DateTime, ForeignKey, Integer, String, func, relationship


class TaskAssignee(Base):
    """Model for assignees of a task."""

    __tablename__ = "task_assignees"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("Task", back_populates="assignees")
