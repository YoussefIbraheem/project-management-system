from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .. import logger
from . import Base

class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(String, nullable=False)

    project = relationship("Project", back_populates="members")
    
    

class TaskAssignee(Base):
    __tablename__ = "task_assignees"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(String, nullable=False)

    task = relationship("Task", back_populates="assignees")