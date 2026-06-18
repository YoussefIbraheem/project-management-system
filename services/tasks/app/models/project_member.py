from . import (
    Base,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
    relationship,
)


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

    __table_args__ = (UniqueConstraint("project_id", "user_id"),)
