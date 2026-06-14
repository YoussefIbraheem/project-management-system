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
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500


@document(response_schema=BoardResponse)
@board_bp.route("/<int:board_id>", methods=["GET"])
def board_get(board_id: int):
    """
    Retrieve a specific board by its ID.
    """

    try:
        board_id = request.view_args["board_id"]
        board = get_board_by_id(board_id=board_id)

        return jsonify(board.model_dump()), 200
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500


@document(
    request_schema=BoardCreate,
    response_schema=BoardResponse,
)
@board_bp.route("/", methods=["POST"])
def board_create():
    """
    Create a new board.
    """

    data = request.get_json()

    if not data:
        return jsonify({"error": "No Data Provided"}), 400

    try:
        board_data = BoardCreate(**data)
        created_board = create_board(board_data=board_data)
        return jsonify(created_board.model_dump())
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500


@document(
    request_schema=BoardUpdate,
    response_schema=BoardResponse,
)
@board_bp.route("/<int:board_id>", methods=["PUT"])
def board_update(board_id: int):
    """
    Update a specific board by its ID.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No Data Provided"}), 400

    try:
        board_data = BoardUpdate(**data)
        updated_board = update_board(board_id=board_id, board_data=board_data)
        return jsonify(updated_board.model_dump())
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500


@board_bp.route("/<int:board_id>", methods=["DELETE"])
def board_delete(board_id: int):
    """
    Delete a specific board by its ID.
    """

    try:
        success = delete_board(board_id=board_id)

        if not success:
            return jsonify({"error": "tests/board_test.py::test_board_update_returns_updated_boardd"}), 404

        return jsonify({"message": "Board Deleted Successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500
