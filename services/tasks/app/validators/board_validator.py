from utils.exceptions import InternalServerException, NotFoundException

from app.models import Board, BoardColumn
from app.models.board_column import StatusGroup


def get_board_or_404(db, board_id: int) -> Board:
    """
    Retrieve a board by its ID or raise a 404 error if it doesn't exist.

    :param db: SQLAlchemy database session
    :param board_id: The ID of the board to retrieve
    :return: The Board object
    """
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise NotFoundException(f"Board with id {board_id} does not exist")
    return board

def create_default_columns(db, board_id) -> None:
    """
    Create default columns for a given board ID.

    :param db: SQLAlchemy database session
    :param board_id: The ID of the board to create columns for
    """
    board_id = int(board_id)
    try:
        for column in StatusGroup:
            db.add(
                BoardColumn(
                    board_id=board_id,
                    slug=column.db_value,
                    label=column.label,
                    status_group=column.db_value,
                )
            )
    except Exception as e:
        raise InternalServerException(
            f"Failed to create default columns for board {board_id}: {e}"
        )

def get_column_or_404(db, board_id: int, column_id: int)-> BoardColumn:
    """
    Retrieve a column by its ID or raise a 404 error if it does not exist.

    :param db: SQLAlchemy database session
    :param board_id: The ID of the board to check columns for
    :param column_id: The ID of the column to retrieve
    """
    column = db.query(BoardColumn).filter_by(board_id=board_id, id=column_id).first()
    if not column:
        raise NotFoundException("Column not found")
    return column


def ensure_column_not_duplicate(db, board_id: int, slug: str):
    """
    Ensure that a column does not have a duplicate slug within the same board.

    db: SQLAlchemy database session
    board_id: The ID of the board to check columns for
    slug: The slug of the column to ensure uniqueness
    """
    existing_column = (
        db.query(BoardColumn).filter_by(board_id=board_id, slug=slug).first()
    )
    if existing_column:
        raise ValueError("Column with the same title already exists")

    return True
