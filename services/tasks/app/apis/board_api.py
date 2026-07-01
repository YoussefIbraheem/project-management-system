from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
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
    ],  # type: ignore
    response_schema=BoardResponse,  # type: ignore
)
@board_bp.route("/", methods=["GET"])
@jwt_required()
def boards_get():
    try:
        project_id = request.args.get("project_id")
        limit = request.args.get("limit")
        offset = request.args.get("offset")
        boards = get_board_by_project(project_id=project_id, limit=limit, offset=offset)  # type: ignore
        return jsonify([board.model_dump() for board in boards]), 200
    except APIException as e:
        return e.to_response()


@document(response_schema=BoardResponse)  # type: ignore
@board_bp.route("/<int:board_id>", methods=["GET"])
@jwt_required()
def board_get(board_id: int):
    try:
        board = get_board_by_id(board_id=board_id)
        return jsonify(board.model_dump()), 200  # type: ignore
    except APIException as e:
        return e.to_response()


@document(request_schema=BoardCreate, response_schema=BoardResponse)  # type: ignore
@board_bp.route("/", methods=["POST"])
@jwt_required()
def board_create():
    data = request.get_json()
    try:
        if not data:
            raise BadRequestException(message="No Data Provided")
        board_data = BoardCreate(**data)
        created_board = create_board(board_data=board_data)
        return jsonify(created_board.model_dump()), 201
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data=e.errors(),  # type: ignore
        ).to_response()
    except APIException as e:
        return e.to_response()


@document(request_schema=BoardUpdate, response_schema=BoardResponse)  # type: ignore
@board_bp.route("/<int:board_id>", methods=["PUT"])
@jwt_required()
def board_update(board_id: int):
    data = request.get_json()
    try:
        if not data:
            raise BadRequestException(message="No Data Provided")
        board_data = BoardUpdate(**data)
        updated_board = update_board(board_id=board_id, board_data=board_data)
        return jsonify(updated_board.model_dump()), 200  # type: ignore
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data=e.errors(),  # type: ignore
        ).to_response()
    except APIException as e:
        return e.to_response()


@board_bp.route("/<int:board_id>", methods=["DELETE"])
@jwt_required()
def board_delete(board_id: int):
    try:
        success = delete_board(board_id=board_id)

        if not success:
            return NotFoundException(message="Board not found").to_response()

        return jsonify(
            {"message": f"Board with id {board_id} deleted successfully"}
        ), 200

    except APIException as e:
        return e.to_response()


@document(response_schema=BoardColumnDetailsResponse)  # type: ignore
@jwt_required()
@board_bp.route("/<int:board_id>/columns", methods=["GET"])
def columns_get(board_id: int):
    try:
        columns = get_columns(board_id)
        return jsonify([c.model_dump() for c in columns]), 200
    except APIException as e:
        return e.to_response()


@document(response_schema=BoardColumnDetailsResponse)  # type: ignore
@jwt_required()
@board_bp.route("/<int:board_id>/columns/<int:column_id>", methods=["GET"])
def column_get(board_id: int, column_id: int):
    try:
        column = get_column(board_id, column_id)
        return jsonify(column.model_dump()), 200
    except APIException as e:
        return e.to_response()


@document(request_schema=BoardColumnCreate, response_schema=BoardColumnDetailsResponse)  # type: ignore
@jwt_required()
@board_bp.route("/<int:board_id>/columns", methods=["POST"])
def column_create(board_id: int):
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")

        column = create_column(board_id, data)
        return jsonify(column.model_dump()), 201

    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data=e.errors(),  # type: ignore
        ).to_response()
    except APIException as e:
        return e.to_response()


@jwt_required()
@board_bp.route("/<int:board_id>/columns/<int:column_id>", methods=["DELETE"])
def column_delete(board_id: int, column_id: int):
    try:
        delete_column(board_id, column_id)
        return jsonify({"message": "Column deleted successfully"}), 204

    except APIException as e:
        return e.to_response()
