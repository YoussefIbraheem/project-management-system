from app.models import BoardColumn


def get_column_or_404(db,board_id:int, column_id: int):
    column = db.query(BoardColumn).filter_by(board_id=board_id, id=column_id).first()
    if not column:
        raise ValueError("Column not found")
    return column

def ensure_column_not_duplicate(db, board_id: int, slug: str):
    existing_column = db.query(BoardColumn).filter_by(board_id=board_id, slug=slug).first()
    if existing_column:
        raise ValueError("Column with the same title already exists")