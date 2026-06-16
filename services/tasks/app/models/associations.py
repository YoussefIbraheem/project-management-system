from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base


class MemberRole(Base):
    """Model for member roles in a project."""
    __tablename__ = "member_roles"
    
    id = Column(Integer, primary_key=True)
    slug = Column(String, nullable=False, unique=True)
    label = Column(String, nullable=False)


class ProjectMember(Base):
    """Model for members in a project."""
    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("member_roles.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="members")
    role = relationship("MemberRole", back_populates="members")


class TaskAssignee(Base):
    """Model for assignees of a task."""
    __tablename__ = "task_assignees"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship("Task", back_populates="assignees")


class BoardColumn(Base):
    __tablename__ = "board_columns"

    id = Column(Integer, primary_key=True)
    board_id = Column(ForeignKey("boards.id"), index=True, nullable=False)
    slug = Column(String(50), nullable=False)
    label = Column(String(100), nullable=False)
    status_group = Column(String(20), nullable=False) 
    
    board = relationship("Board", back_populates="columns")

    __table_args__ = (
        UniqueConstraint("board_id", "slug"),
        CheckConstraint("status_group IN ('todo', 'in_progress', 'done', 'cancelled')", name="check_status_group")
    )
