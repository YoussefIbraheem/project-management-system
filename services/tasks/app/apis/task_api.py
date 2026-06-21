from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError
from utils.exceptions import (
    APIException,
    ValidationException,
)
from utils.openapi.decorators import document
from utils.publisher import publish_history_event

from app.events.task_event import TaskCreatedEvent, TaskDeletedEvent, TaskUpdatedEvent
from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate, TaskAssign, TaskUnassign
from app.services.task_service import (
    assign_task,
    create_task,
    delete_task,
    get_task_by_id,
    get_tasks,
    unassign_task,
    update_task,
)

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
        logged_in_user = get_jwt_identity()
        data["creator_id"] = logged_in_user
        task_data = TaskCreate(**data)
        created_task = create_task(task_data=task_data)
    except ValidationError as e:
        return ValidationException(
            message="Validation Error", data=e.errors()
        ).to_response()
    except APIException as e:
        return e.to_response()
    else:
        # event = TaskCreatedEvent(
        #     actor_id=get_jwt_identity(),
        #     subject_id=str(created_task.id),
        #     board_id=str(created_task.board_id),
        #     title=created_task.title,
        #     description=created_task.description,
        #     status=created_task.status,
        # )
        # publish_history_event(event.to_dict())
        return jsonify(created_task.model_dump()), 201


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
    except ValidationError as e:
        return ValidationException(
            message="Validation Error", data=e.errors()
        ).to_response()
    except APIException as e:
        return e.to_response()
    else:
        event = TaskUpdatedEvent(
            actor_id=get_jwt_identity(),
            subject_id=str(updated_task.id),
            board_id=str(updated_task.board_id),
            updated_fields=[
                {"name": field, "new_value": getattr(updated_task, field)}
                for field in task_data.model_fields_set
                if getattr(task_data, field) is not None
            ],
        )
        publish_history_event(event.to_dict())
        return jsonify(updated_task.model_dump()), 200


@task_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required()
def task_delete(task_id: int):
    """
    Delete a task by its ID.
    """

    try:
        success = delete_task(task_id=task_id)

        if not success:
            return jsonify({"error": "Task not found"}), 404
    except APIException as e:
        return e.to_response()
    else:
        event = TaskDeletedEvent(
            actor_id=get_jwt_identity(),
            subject_id=str(task_id),
        )
        publish_history_event(event.to_dict())
        return jsonify({"message": f"Task with id {task_id} has been deleted!"}), 200

@document(request_schema=TaskAssign,response_schema=TaskResponse)
@task_bp.route("/<int:task_id>/assign", methods=["POST"])
@jwt_required()
def task_assign(task_id):
    try:
        data = request.get_json()
        assignees_ids = data.get("assignees_ids",[])
        task = assign_task(task_id=task_id, assignees_ids=assignees_ids)
        return jsonify(task.model_dump())
    except APIException as e:
        return e.to_response()


@document(request_schema=TaskUnassign,response_schema=TaskResponse)
@task_bp.route("/<int:task_id>/unassign", methods=["POST"])
@jwt_required()
def task_unassign(task_id):
    try:
        data = request.get_json()
        assignees_ids = data.get("assignees_ids",[])
        task = unassign_task(task_id=task_id, assignees_ids=assignees_ids)
        return jsonify(task.model_dump())
    except APIException as e:
        return e.to_response()
