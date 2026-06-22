from app.db.database import get_db_session
from app.models import BoardColumn
from app.schemas.board_column_schema import BoardColumnDetailsResponse
from app.validators.board_column_validator import (
    ensure_column_not_duplicate,
    get_column_or_404,
)
from app.validators.board_validator import ensure_board_exists


def get_columns(board_id: int):
    """
    Retrieve all columns for a given board.

    Args:
        board_id (int): The ID of the board.

    Returns:
        list[BoardColumnDetailsResponse]: A list of column details.
    """
    with get_db_session() as db:
        columns = db.query(BoardColumn).filter(BoardColumn.board_id==board_id).all()
        return [BoardColumnDetailsResponse.model_validate(column) for column in columns]


def get_column(board_id: int, column_id: int):
    """
    Retrieve a specific column for a given board.

    Args:
        board_id (int): The ID of the board.
        column_id (int): The ID of the column.

    Returns:
        BoardColumnDetailsResponse: The details of the column.
    """
    with get_db_session() as db:
        column = get_column_or_404(db, board_id, column_id)
        return BoardColumnDetailsResponse.model_validate(column)


def create_column(board_id: int, data: dict):
    """
    Create a new column for a given board.

    Args:
        board_id (int): The ID of the board.
        data (dict): The data to create the column with.

    Returns:
        BoardColumnDetailsResponse: The details of the newly created column.
    """
    with get_db_session() as db:
        ensure_board_exists(db, board_id)
        ensure_column_not_duplicate(db, board_id, data["slug"])
        new_column = BoardColumn(**data, board_id=board_id)
        db.add(new_column)
        db.commit()
        db.refresh(new_column)
        return BoardColumnDetailsResponse.model_validate(new_column)


def delete_column(board_id: int, column_id: int):
    """
    Delete a specific column for a given board.

    Args:
        board_id (int): The ID of the board.
        column_id (int): The ID of the column.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    with get_db_session() as db:
        ensure_board_exists(db, board_id)
        column = get_column_or_404(db, board_id, column_id)
        db.delete(column)
        db.commit()

        return True
