from app.schemas.board_schema import BoardCreate, BoardUpdate, BoardResponse
from app.services.board_service import (
    create_board,
    update_board,
    get_board_by_id,
    get_board_by_project,
    delete_board,
)
from flask import Blueprint, jsonify, request
from utils.openapi.decorators import document
from utils.exceptions import (
    APIException,
    BadRequestException,
    ValidationException,
    NotFoundException,
)
from utils.publisher import publish_history_event
from app.events.board_event import (
    BoardCreatedEvent,
    BoardUpdatedEvent,
    BoardDeletedEvent,
)
from pydantic import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

board_bp = Blueprint("board", __name__, url_prefix="/api/v1/boards/")


@document(
    query_params=[
        {
            "name": "project_id",
            "type": "string",
            "required": True,
            "description": "The ID of the project for which to retrieve boards",
        },
        {
            "name": "limit",
            "type": "integer",
            "required": False,
            "description": "The maximum number of boards to retrieve",
        },
        {
            "name": "offset",
            "type": "integer",
            "required": False,
            "description": "The offset for pagination",
        },
    ],
    response_schema=BoardResponse,
)
@board_bp.route("/", methods=["GET"])
@jwt_required()
def boards_list():
    """
    Retrieve a list of boards for a specific project.
    """

    try:
        project_id = request.args.get("project_id")
        limit = request.args.get("limit")
        offset = request.args.get("offset")

        boards = get_board_by_project(project_id=project_id, limit=limit, offset=offset)

        data = [board.model_dump() for board in boards]

        return jsonify(data), 200
    except APIException as e:
        return e.to_response()


@document(response_schema=BoardResponse)
@board_bp.route("/<int:board_id>", methods=["GET"])
@jwt_required()
def board_get(board_id: int):
    """
    Retrieve a specific board by its ID.
    """

    try:
        board_id = request.view_args["board_id"]
        board = get_board_by_id(board_id=board_id)

        return jsonify(board.model_dump()), 200
    except APIException as e:
        return e.to_response()


@document(
    request_schema=BoardCreate,
    response_schema=BoardResponse,
)
@board_bp.route("/", methods=["POST"])
@jwt_required()
def board_create():
    """
    Create a new board.
    """

    data = request.get_json()

    if not data:
        return BadRequestException(message="No Data Provided").to_response()

    try:
        board_data = BoardCreate(**data)
        created_board = create_board(board_data=board_data)
    except ValidationError as e:
        return ValidationException(
            message="Validation Error", data=e.errors()
        ).to_response()
    except APIException as e:
        return e.to_response()
    else:
        event = BoardCreatedEvent(
            actor_id=get_jwt_identity(),
            subject_id=str(created_board.id),
            project_id=str(created_board.project_id),
            name=created_board.name,
            description=created_board.description,
            columns=[col for col in created_board.columns],
        )
        publish_history_event(event.to_dict())
        return jsonify(created_board.model_dump()) , 201


@document(
    request_schema=BoardUpdate,
    response_schema=BoardResponse,
)
@board_bp.route("/<int:board_id>", methods=["PUT"])
@jwt_required()
def board_update(board_id: int):
    """
    Update a specific board by its ID.
    """
    data = request.get_json()

    if not data:
        return BadRequestException(message="No Data Provided").to_response()

    try:
        board_data = BoardUpdate(**data)
        updated_board = update_board(board_id=board_id, board_data=board_data)
    except ValidationError as e:
        return ValidationException(
            message="Validation Error", data=e.errors()
        ).to_response()
    except APIException as e:
        return e.to_response()
    else:
        event = BoardUpdatedEvent(
            actor_id=get_jwt_identity(),
            subject_id=str(updated_board.id),
            project_id=str(updated_board.project_id),
            updated_fields=[
                {"name": field, "new_value": getattr(updated_board, field)}
                for field in board_data.model_fields_set
                if getattr(board_data, field) is not None
            ],
        )
        publish_history_event(event.to_dict())
        return jsonify(updated_board.model_dump()), 200


@board_bp.route("/<int:board_id>", methods=["DELETE"])
@jwt_required()
def board_delete(board_id: int):
    """
    Delete a specific board by its ID.
    """

    try:
        success = delete_board(board_id=board_id)

        if not success:
            return NotFoundException(message="Board not found").to_response()
    except APIException as e:
        return e.to_response()
    else:
        event = BoardDeletedEvent(
            actor_id=get_jwt_identity(),
            subject_id=str(board_id),
        )
        publish_history_event(event.to_dict())
        return (
            jsonify({"message": f"Board with id {board_id} deleted successfully"}),
            200,
        )
