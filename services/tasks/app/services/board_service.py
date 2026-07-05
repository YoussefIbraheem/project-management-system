from cProfile import label
from typing import List, Optional

from slugify import slugify

from app import logger
from app.db.database import get_db_session
from app.models import Board, BoardColumn
from app.permissions.board_permission import (
    can_create_board,
    can_create_board_column,
    can_delete_board,
    can_delete_board_column,
    can_update_board,
    can_update_board_column,
    can_view_board,
    can_view_board_column,
    can_view_board_columns,
    can_view_boards,
)
from app.schemas.board_column_schema import (
    BoardColumnCreate,
    BoardColumnDetailsResponse,
)
from app.schemas.board_schema import BoardCreate, BoardResponse, BoardUpdate
from app.security.actor import Actor
from app.validators.board_validator import (
    create_default_columns,
    ensure_column_not_duplicate,
    get_board_or_404,
    get_column_or_404,
)
from app.validators.project_validator import get_member_or_404, get_project_or_404


def get_board_by_project(
    actor: Actor, project_id: int, limit: int = 50, offset: int = 0
) -> List[BoardResponse]:
    """
    Retrieve a paginated list of boards associated with a specific project.
    Args:
        project_id (int): The ID of the project to retrieve boards for.
        limit (int, optional): The maximum number of boards to return. Defaults to 50.
        offset (int, optional): The number of boards to skip before collecting results. Defaults to 0.
    Returns:
        List[BoardResponse]: A list of BoardResponse objects representing the boards for the project.
    Raises:
        ValueError: If the project with the specified ID does not exist.
    """
    with get_db_session() as db:
        can_view_boards(db, actor, project_id)

        db_boards = (
            db.query(Board)
            .filter(Board.project_id == project_id)
            .limit(limit)
            .offset(offset)
            .all()
        )

        return [BoardResponse.model_validate(board) for board in db_boards]


def get_board_by_id(actor: Actor, board_id: int) -> Optional[BoardResponse]:
    """
    Get Board Details

    Args:
        board_id (int): The ID of the board to retrieve

    Raises:
        ValueError: If the board with the given ID does not exist

    Returns:
        Optional[BoardResponse]: The board details if found, otherwise None
    """
    with get_db_session() as db:
        db_board = get_board_or_404(db, board_id)

        can_view_board(db, actor, db_board.project_id)

        return BoardResponse.model_validate(db_board)


def create_board(actor: Actor, board_data: BoardCreate) -> BoardResponse:
    """
    Create Board

    Args:
        board_data (BoardCreate): The data for the board to be created

    Returns:
        BoardResponse: The created board details
    """
    with get_db_session() as db:
        project = get_project_or_404(db, board_data.project_id)

        can_create_board(db, actor, project.id)

        db_board = Board(
            name=board_data.name,
            description=board_data.description,
            project_id=project.id,
        )

        db.add(db_board)
        db.flush()
        db.refresh(db_board)

        if board_data.default_columns:
            create_default_columns(db, db_board.id)

        return BoardResponse.model_validate(db_board)


def update_board(
    actor: Actor, board_id: int, board_data: BoardUpdate
) -> Optional[BoardResponse]:
    """
    Update an existing board.
    Args:
        board_id (int): The ID of the board to update
        board_data (BoardUpdate): The updated board data

    Raises:
        ValueError: If the board with the given ID does not exist
    Returns:
        Optional[BoardResponse]: The updated board details if the update was successful, or None if the board was not found
    """
    with get_db_session() as db:
        db_board = get_board_or_404(db, board_id)

        can_update_board(db, actor, db_board)

        if board_data.name is not None:
            db_board.name = board_data.name  # type: ignore[assignment]

        if board_data.description is not None:
            db_board.description = board_data.description  # type: ignore[assignment]

        db.flush()
        db.refresh(db_board)

        return BoardResponse.model_validate(db_board)


def delete_board(actor: Actor, board_id: int) -> bool:
    """
    Delete Board

    Args:
        board_id (int): The ID of the board to delete

    Raises:
        ValueError: If the board with the given ID does not exist

    Returns:
        bool: True if the board was deleted successfully, False otherwise
    """
    with get_db_session() as db:
        db_board = get_board_or_404(db, board_id)

        can_delete_board(db, actor, db_board)

        db.delete(db_board)
        db.flush()

        return True


# Board Member


def get_columns(actor: Actor, board_id: int):
    """
    Retrieve all columns for a given board.

    Args:
        board_id (int): The ID of the board.

    Returns:
        list[BoardColumnDetailsResponse]: A list of column details.
    """
    with get_db_session() as db:
        board = get_board_or_404(db, board_id)

        can_view_board_columns(db, actor, board)

        columns = db.query(BoardColumn).filter(BoardColumn.board_id == board.id).all()
        return [BoardColumnDetailsResponse.model_validate(column) for column in columns]


def get_column(actor: Actor, board_id: int, column_id: int):
    """
    Retrieve a specific column for a given board.

    Args:
        board_id (int): The ID of the board.
        column_id (int): The ID of the column.

    Returns:
        BoardColumnDetailsResponse: The details of the column.
    """
    with get_db_session() as db:
        board = get_board_or_404(db, board_id)

        can_view_board_column(db, actor, board)

        column = get_column_or_404(db, board_id, column_id)
        return BoardColumnDetailsResponse.model_validate(column)


def create_column(actor: Actor, board_id: int, board_column_data: BoardColumnCreate):
    """
    Create a new column for a given board.

    Args:
        board_id (int): The ID of the board.
        data (dict): The data to create the column with.

    Returns:
        BoardColumnDetailsResponse: The details of the newly created column.
    """
    with get_db_session() as db:
        board = get_board_or_404(db, board_id)

        can_create_board_column(db, actor, board)

        ensure_column_not_duplicate(db, board.id, board_column_data.label)  # type: ignore[assignment]
        new_column = BoardColumn(
            label=board_column_data.label,
            slug=slugify(board_column_data.label),
            status_group=board_column_data.status_group,
        )

        db.add(new_column)
        db.commit()
        db.refresh(new_column)
        return BoardColumnDetailsResponse.model_validate(new_column)


def delete_column(actor: Actor, board_id: int, column_id: int):
    """
    Delete a specific column for a given board.

    Args:
        board_id (int): The ID of the board.
        column_id (int): The ID of the column.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    with get_db_session() as db:
        board = get_board_or_404(db, board_id)

        can_delete_board_column(db, actor, board)

        column = get_column_or_404(db, board.id, column_id)  # type: ignore

        db.delete(column)
        db.commit()

        return True
