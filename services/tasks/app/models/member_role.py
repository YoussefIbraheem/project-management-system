from . import Base, Column, DateTime, Integer, String, func, relationship


class MemberRole(Base):
    """Model for member roles in a project."""

    __tablename__ = "member_roles"

    id = Column(Integer, primary_key=True)
    slug = Column(String, nullable=False, unique=True)
    label = Column(String, nullable=False)

    project_members = relationship(
        "ProjectMember", back_populates="role", cascade="all, delete-orphan"
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
