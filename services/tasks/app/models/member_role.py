from . import Base, Column, Integer, String


class MemberRole(Base):
    """Model for member roles in a project."""

    __tablename__ = "member_roles"

    id = Column(Integer, primary_key=True)
    slug = Column(String, nullable=False, unique=True)
    label = Column(String, nullable=False)
