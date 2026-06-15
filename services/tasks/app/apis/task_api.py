from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskStats, TaskResponse
from app.services.task_service import (
    get_tasks,
    get_task_by_id,
    create_task,
    update_task,
    delete_task,
)
from flask import jsonify, request, Blueprint
from utils.openapi.decorators import document
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.exceptions import (
    BadRequestException,
    NotFoundException,
    APIException,
    ValidationException,
)
from pydantic import ValidationError

task_bp = Blueprint("task", __name__, url_prefix="/api/v1/tasks/")


@document(
    query_params=[
        {
            "name": "board_id",
            "type": "integer",
            "required": False,
            "description": "The ID of the board for which to retrieve tasks",
        },
        {
            "name": "user_id",
            "type": "string",
            "required": False,
            "description": "The ID of the user for which to retrieve tasks",
        },
        {
            "name": "assigned_to",
            "type": "string",
            "required": False,
            "description": "The ID of the assignee for which to retrieve tasks",
        },
        {
            "name": "status",
            "type": "string",
            "required": False,
            "description": "The status of the tasks to retrieve",
        },
        {
            "name": "priority",
            "type": "string",
            "required": False,
            "description": "The priority of the tasks to retrieve",
        },
        {
            "name": "limit",
            "type": "integer",
            "required": False,
            "description": "The maximum number of tasks to retrieve",
        },
        {
            "name": "offset",
            "type": "integer",
            "required": False,
            "description": "The offset for pagination",
        },
    ],
    response_schema=TaskResponse,
)
@task_bp.route("/", methods=["GET"])
@jwt_required()
def tasks_list():
    """
    Retrieve a list of tasks based on optional query parameters.
    """

    try:
        board_id = request.args.get("board_id")
        user_id = request.args.get("user_id")
        assigned_to = request.args.get("assigned_to")
        status = request.args.get("status")
        priority = request.args.get("priority")
        limit = request.args.get("limit")
        offset = request.args.get("offset")

        tasks = get_tasks(
            board_id, user_id, assigned_to, status, priority, limit, offset
        )

        data = [task.model_dump() for task in tasks]

        return jsonify(data), 200

    except APIException as e:
        return e.to_response()


@document(response_schema=TaskResponse)
@task_bp.route("/<int:task_id>", methods=["GET"])
@jwt_required()
def task_get(task_id: int):
    """
    Retrieve a specific task by its ID.
    """

    try:
        task_id = request.view_args["task_id"]
        task = get_task_by_id(task_id=task_id)
        return jsonify(task.model_dump()), 200
    except APIException as e:
        return e.to_response()


@document(
    request_schema=TaskCreate,
    response_schema=TaskResponse,
)
@task_bp.route("/", methods=["POST"])
@jwt_required()
def task_create():
    """
    Create a new task.
    """

    data = request.get_json()
    if not data:
        return jsonify({"error": "No Data Provided"})
    try:

        task_data = TaskCreate(**data)
        created_task = create_task(task_data=task_data)
        return jsonify(created_task.model_dump())
    except ValidationError as e:
        return ValidationException(
            message="Validation Error", data=e.errors()
        ).to_response()
    except APIException as e:
        return e.to_response()


@document(
    request_schema=TaskUpdate,
    response_schema=TaskResponse,
)
@task_bp.route("/<int:task_id>", methods=["PUT"])
@jwt_required()
def task_update(task_id):
    """
    Update an existing task.
    """

    data = request.get_json()
    if not data:
        return jsonify({"error": "No Data Provided"}), 400

    try:
        task_data = TaskUpdate(**data)
        updated_task = update_task(task_id=task_id, task_data=task_data)
        return jsonify(updated_task.model_dump())
    except ValidationError as e:
        return ValidationException(
            message="Validation Error", data=e.errors()
        ).to_response()
    except APIException as e:
        return e.to_response()


@task_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required()
def task_delete(task_id: int):
    """
    Delete a task by its ID.
    """

    try:
        success = delete_task(task_id=task_id)

        if not success:
            return jsonify({"error": "Task not found!"}), 404
        return jsonify({"message": "Task deleted successfully!"}), 200
    except APIException as e:
        return e.to_response()
