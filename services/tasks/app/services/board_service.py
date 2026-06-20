from typing import List, Optional

from utils.exceptions import APIException, NotFoundException , InternalServerException

from app.db.database import get_db_session
from app.models import Board, BoardColumn, Project
from app.models.board_column import StatusGroup
from app.schemas.board_schema import BoardCreate, BoardResponse, BoardUpdate


def get_board_by_project(
    project_id: int, limit: int = 50, offset: int = 0
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
        db_boards = (
            db.query(Board)
            .filter(Board.project_id == project_id)
            .limit(limit)
            .offset(offset)
            .all()
        )

        return [BoardResponse.model_validate(board) for board in db_boards]


def get_board_by_id(board_id: int) -> Optional[BoardResponse]:
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
        db_board = db.query(Board).filter(Board.id == board_id).first()

        if not db_board:
            raise NotFoundException(f"Board with id {board_id} does not exist")

        return BoardResponse.model_validate(db_board)


def create_board(board_data: BoardCreate) -> BoardResponse:
    """
    Create Board

    Args:
        board_data (BoardCreate): The data for the board to be created

    Returns:
        BoardResponse: The created board details
    """

    with get_db_session() as db:
        project = db.query(Project).filter(Project.id == board_data.project_id).first()

        if not project:
            raise NotFoundException(
                f"Project with id {board_data.project_id} does not exist"
            )

        db_board = Board(
            name=board_data.name,
            description=board_data.description,
            project_id=board_data.project_id,
        )

        db.add(db_board)
        db.flush()
        db.refresh(db_board)
        db.commit()
        

        if board_data.default_columns:
            try:
                with db.begin():
                    for column in StatusGroup:
                        
                        db_board_column = BoardColumn(
                            board_id=db_board.id,
                            slug=column.db_value,
                            label=column.label,
                            status_group=column.db_value,
                        )
                        db.add(db_board_column)
            except Exception as e:
                db.rollback()
                raise InternalServerException(f"Failed to create default columns for board {db_board.id}: {e}")

        return BoardResponse.model_validate(db_board)


def update_board(board_id: int, board_data: BoardUpdate) -> Optional[BoardResponse]:
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
        db_board = db.query(Board).filter(Board.id == board_id).first()

        if not db_board:
            raise NotFoundException(f"Board with id {board_id} does not exist")

        if board_data.name is not None:
            db_board.name = board_data.name

        if board_data.description is not None:
            db_board.description = board_data.description

        db.flush()
        db.refresh(db_board)

        return BoardResponse.model_validate(db_board)


def delete_board(board_id: int) -> bool:
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
        db_board = db.query(Board).filter(Board.id == board_id).first()

        if not db_board:
            return False

        db.delete(db_board)
        db.flush()

        return True
