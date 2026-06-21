from utils.exceptions import InternalServerException, NotFoundException

from app.models import Board, BoardColumn
from app.models.board_column import StatusGroup


def get_board_or_404(db, board_id: int) -> Board:
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise NotFoundException(f"Board with id {board_id} does not exist")
    return board


def ensure_board_exists(db, board_id: int) -> Board:
    return get_board_or_404(db, board_id)


def create_default_columns(db, board_id) -> None:
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
