from . import Base, Column, Integer, String, relationship


class MemberRole(Base):
    """Model for member roles in a project."""

    __tablename__ = "member_roles"

    id = Column(Integer, primary_key=True)
    slug = Column(String, nullable=False, unique=True)
    label = Column(String, nullable=False)

    project_members = relationship("ProjectMember", back_populates="role")
