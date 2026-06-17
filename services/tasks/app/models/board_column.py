from . import Base, Column, Integer, String, ForeignKey, relationship, UniqueConstraint, CheckConstraint

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
