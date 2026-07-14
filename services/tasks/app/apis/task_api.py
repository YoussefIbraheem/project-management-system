from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError
from shared.exceptions import APIException, BadRequestException, ValidationException
from shared.openapi.decorators import document

from app.schemas.task_schema import (
    TaskAssign,
    TaskCreate,
    TaskResponse,
    TaskUnassign,
    TaskUpdate,
)
from app.services.task_service import (
    assign_task,
    create_task,
    delete_task,
    get_task_by_id,
    get_tasks,
    unassign_task,
    update_task,
)

from . import get_actor

task_bp = Blueprint("task", __name__, url_prefix="/api/v1/tasks/")


@document(
    query_params=[
        {
            "name": "project_id",
            "type": "integer",
            "required": True,
            "description": "The ID of the project for which to retrieve tasks",
        },
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
    ],  # type: ignore
    response_schema=TaskResponse,  # type: ignore
)
@task_bp.route("/", methods=["GET"])
@jwt_required()
def tasks_list():
    try:
        project_id = request.args.get("project_id")
        board_id = request.args.get("board_id")
        user_id = request.args.get("user_id")
        assigned_to = request.args.get("assigned_to")
        column_id = request.args.get("column_id")
        priority = request.args.get("priority")
        limit = request.args.get("limit")
        offset = request.args.get("offset")
        actor = get_actor()

        if not project_id:
            raise BadRequestException("Project ID is required")

        tasks = get_tasks(
            actor=actor,
            project_id=project_id,
            board_id=board_id,
            creator_id=user_id,
            assigned_to=assigned_to,
            column_id=column_id,
            priority=priority,
            limit=limit,
            offset=offset,
        )
        return jsonify([task.model_dump() for task in tasks]), 200
    except APIException as e:
        return e.to_response()


@document(response_schema=TaskResponse)  # type: ignore
@task_bp.route("/<int:task_id>", methods=["GET"])
@jwt_required()
def task_get(task_id: int):
    try:
        actor = get_actor()
        task = get_task_by_id(actor=actor, task_id=task_id)
        return jsonify(task.model_dump()), 200
    except APIException as e:
        return e.to_response()


@document(request_schema=TaskCreate, response_schema=TaskResponse)  # type: ignore
@task_bp.route("/", methods=["POST"])
@jwt_required()
def task_create():
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")

        data["creator_id"] = get_jwt_identity()
        task_data = TaskCreate(**data)
        actor = get_actor()
        created_task = create_task(actor=actor, task_data=task_data)
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data=e.errors(),  # type: ignore
        ).to_response()
    except APIException as e:
        return e.to_response()
    else:
        return jsonify(created_task.model_dump()), 201


@document(request_schema=TaskUpdate, response_schema=TaskResponse)  # type: ignore
@task_bp.route("/<int:task_id>", methods=["PUT"])
@jwt_required()
def task_update(task_id):
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")

        actor = get_actor()
        task_data = TaskUpdate(**data)
        updated_task = update_task(actor=actor, task_id=task_id, task_data=task_data)
        return jsonify(updated_task.model_dump()), 200
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data=e.errors(),  # type: ignore
        ).to_response()
    except APIException as e:
        return e.to_response()


@task_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required()
def task_delete(task_id: int):
    try:
        actor = get_actor()
        success = delete_task(actor=actor, task_id=task_id)
        if not success:
            return jsonify({"error": "Task not found"}), 404
        return jsonify({"message": f"Task with id {task_id} has been deleted!"}), 200
    except APIException as e:
        return e.to_response()


@document(request_schema=TaskAssign, response_schema=TaskResponse)  # type: ignore
@task_bp.route("/<int:task_id>/assign", methods=["POST"])
@jwt_required()
def task_assign(task_id):
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")
        actor = get_actor()
        task_assign_data = TaskAssign(**data)
        task = assign_task(
            actor=actor, task_id=task_id, assignees_ids=task_assign_data.assignees_ids
        )
        return jsonify(task.model_dump()), 200
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data=e.errors(),  # type: ignore
        ).to_response()
    except APIException as e:
        return e.to_response()


@document(request_schema=TaskUnassign, response_schema=TaskResponse)  # type: ignore
@task_bp.route("/<int:task_id>/unassign", methods=["POST"])
@jwt_required()
def task_unassign(task_id):
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")
        actor = get_actor()
        task_unassign_data = TaskUnassign(**data)
        task = unassign_task(
            actor=actor, task_id=task_id, assignees_ids=task_unassign_data.assignees_ids
        )
        return jsonify(task.model_dump()), 200
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data=e.errors(),  # type: ignore
        ).to_response()
    except APIException as e:
        return e.to_response()
