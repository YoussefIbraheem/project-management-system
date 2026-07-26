from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from pydantic import ValidationError
from shared.exceptions import (
    APIException,
    BadRequestException,
    NotFoundException,
    ValidationException,
)
from shared.openapi.decorators import document

from app.schemas.board_column_schema import (
    BoardColumnCreate,
    BoardColumnDetailsResponse,
)
from app.schemas.board_schema import BoardCreate, BoardResponse, BoardUpdate
from app.services.board_service import (
    create_board,
    create_column,
    delete_board,
    delete_column,
    get_board_by_id,
    get_board_by_project,
    get_column,
    get_columns,
    update_board,
)

from . import get_actor

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
def boards_get():
    try:
        project_id = request.args.get("project_id")
        limit = request.args.get("limit")
        offset = request.args.get("offset")
        actor = get_actor()
        boards = get_board_by_project(
            actor=actor,
            project_id=project_id,
            limit=limit,
            offset=offset,
        )
        return jsonify([board.model_dump() for board in boards]), 200
    except APIException as e:
        return e.to_response()


@document(response_schema=BoardResponse)
@board_bp.route("/<int:board_id>", methods=["GET"])
@jwt_required()
def board_get(board_id: int):
    try:
        actor = actor = get_actor()
        board = get_board_by_id(actor=actor, board_id=board_id)
        return jsonify(board.model_dump()), 200
    except APIException as e:
        return e.to_response()


@document(request_schema=BoardCreate, response_schema=BoardResponse)
@board_bp.route("/", methods=["POST"])
@jwt_required()
def board_create():
    data = request.get_json()
    try:
        if not data:
            raise BadRequestException(message="No Data Provided")
        board_data = BoardCreate(**data)
        actor = get_actor()
        created_board = create_board(actor=actor, board_data=board_data)
        return jsonify(created_board.model_dump()), 201
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data=e.errors(),
        ).to_response()
    except APIException as e:
        return e.to_response()


@document(request_schema=BoardUpdate, response_schema=BoardResponse)
@board_bp.route("/<int:board_id>", methods=["PUT"])
@jwt_required()
def board_update(board_id: int):
    data = request.get_json()
    try:
        if not data:
            raise BadRequestException(message="No Data Provided")
        board_data = BoardUpdate(**data)
        actor = get_actor()
        updated_board = update_board(
            actor=actor, board_id=board_id, board_data=board_data
        )
        return jsonify(updated_board.model_dump()), 200
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data=e.errors(),
        ).to_response()
    except APIException as e:
        return e.to_response()


@board_bp.route("/<int:board_id>", methods=["DELETE"])
@jwt_required()
def board_delete(board_id: int):
    try:
        actor = get_actor()
        success = delete_board(actor=actor, board_id=board_id)

        if not success:
            return NotFoundException(message="Board not found").to_response()

        return (
            jsonify({"message": f"Board with id {board_id} deleted successfully"}),
            200,
        )

    except APIException as e:
        return e.to_response()


@document(response_schema=BoardColumnDetailsResponse)
@board_bp.route("/<int:board_id>/columns", methods=["GET"])
@jwt_required()
def columns_get(board_id: int):
    try:
        actor = get_actor()
        columns = get_columns(actor=actor, board_id=board_id)
        return jsonify([c.model_dump() for c in columns]), 200
    except APIException as e:
        return e.to_response()


@document(response_schema=BoardColumnDetailsResponse)
@board_bp.route("/<int:board_id>/columns/<int:column_id>", methods=["GET"])
@jwt_required()
def column_get(board_id: int, column_id: int):
    try:
        actor = get_actor()
        column = get_column(actor=actor, board_id=board_id, column_id=column_id)
        return jsonify(column.model_dump()), 200
    except APIException as e:
        return e.to_response()


@document(request_schema=BoardColumnCreate, response_schema=BoardColumnDetailsResponse)
@board_bp.route("/<int:board_id>/columns", methods=["POST"])
@jwt_required()
def column_create(board_id: int):
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")
        board_column_data = BoardColumnCreate(**data)
        actor = get_actor()
        column = create_column(
            actor=actor, board_id=board_id, board_column_data=board_column_data
        )
        return jsonify(column.model_dump()), 201

    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data=e.errors(),
        ).to_response()
    except APIException as e:
        return e.to_response()


@board_bp.route("/<int:board_id>/columns/<int:column_id>", methods=["DELETE"])
@jwt_required()
def column_delete(board_id: int, column_id: int):
    try:
        actor = get_actor()
        delete_column(actor=actor, board_id=board_id, column_id=column_id)
        return jsonify({"message": "Column deleted successfully"}), 204

    except APIException as e:
        return e.to_response()
