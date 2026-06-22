from sys import prefix

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError
from utils.exceptions import (
    APIException,
    BadRequestException,
    NotFoundException,
    ValidationException,
)
from utils.openapi.decorators import document
from utils.publisher import publish_history_event

from app.schemas.board_column_schema import BoardColumnCreate, BoardColumnDetailsResponse
from app.services.board_column_service import (
    create_column,
    delete_column,
    get_column,
    get_columns,
)

column_bp = Blueprint("board_column", __name__, url_prefix="/api/v1/boards/")


@document(response_schema=BoardColumnDetailsResponse)
@jwt_required()
@column_bp.route("/<int:board_id>/columns", methods=["GET"])
def columns_get(board_id: int):
    try:
        columns = get_columns(board_id)
        return jsonify([c.model_dump() for c in columns]), 200
    except APIException as e:
        return e.to_response()

@document(response_schema=BoardColumnDetailsResponse)
@jwt_required()
@column_bp.route("/<int:board_id>/columns/<int:column_id>", methods=["GET"])
def column_get(board_id: int, column_id: int):
    try:
        column = get_column(board_id, column_id)
        return jsonify(column.model_dump()), 200
    except APIException as e:
        return e.to_response()


@document(request_schema=BoardColumnCreate,response_schema=BoardColumnDetailsResponse)
@jwt_required()
@column_bp.route("/<int:board_id>/columns", methods=["POST"])
def column_create(board_id: int):
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")

        column = create_column(board_id, data)
        return jsonify(column.model_dump()), 201

    except ValidationError as e:
        return ValidationException(
            message="Validation Error", data=e.errors()
        ).to_response()
    except APIException as e:
        return e.to_response()


@jwt_required()
@column_bp.route("/<int:board_id>/columns/<int:column_id>", methods=["DELETE"])
def column_delete(board_id: int, column_id: int):
    try:
        delete_column(board_id, column_id)
        return jsonify({"message": "Column deleted successfully"}), 204

    except APIException as e:
        return e.to_response()
