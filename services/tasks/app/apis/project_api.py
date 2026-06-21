from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError
from utils.exceptions import APIException, BadRequestException, ValidationException
from utils.openapi.decorators import document
from utils.publisher import publish_history_event

from app.events.project_event import (
    ProjectCreatedEvent,
    ProjectDeletedEvent,
    ProjectUpdatedEvent,
)
from app.schemas.project_schema import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import (
    create_project,
    delete_project,
    get_project_by_id,
    get_projects,
    update_project,
)

project_bp = Blueprint("project", __name__, url_prefix="/api/v1/projects")


@document(
    query_params=[
        {
            "name": "owner_id",
            "type": "string",
            "required": True,
            "description": "Owner ID to filter projects",
        },
        {
            "name": "limit",
            "type": "integer",
            "required": False,
            "description": "Max number of projects to retrieve",
        },
        {
            "name": "offset",
            "type": "integer",
            "required": False,
            "description": "Pagination offset",
        },
    ],
    response_schema=ProjectResponse,
)
@project_bp.route("/", methods=["GET"])
@jwt_required()
def projects_list():
    try:
        limit = request.args.get("limit", 50)
        offset = request.args.get("offset", 0)
        projects = get_projects(limit=int(limit), offset=int(offset))
        return jsonify([p.model_dump() for p in projects]), 200
    except APIException as e:
        return e.to_response()


@document(response_schema=ProjectResponse)
@project_bp.route("/<int:project_id>", methods=["GET"])
@jwt_required()
def project_details(project_id: int):
    try:
        project = get_project_by_id(project_id=project_id)
        return jsonify(project.model_dump()), 200
    except APIException as e:
        return e.to_response()


@document(request_schema=ProjectCreate, response_schema=ProjectResponse)
@project_bp.route("/", methods=["POST"])
@jwt_required()
def project_create():
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")
        project_data = ProjectCreate(**data)
        project = create_project(project_data=project_data)
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data={err["loc"][0]: err["msg"] for err in e.errors()},
        ).to_response()
    except APIException as e:
        return e.to_response()
    return jsonify(project.model_dump()), 201


@document(request_schema=ProjectUpdate, response_schema=ProjectResponse)
@project_bp.route("/<int:project_id>", methods=["PUT"])
@jwt_required()
def project_update(project_id: int):
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")
        project_data = ProjectUpdate(**data)
        project = update_project(project_id=project_id, project_data=project_data)
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data={err["loc"][0]: err["msg"] for err in e.errors()},
        ).to_response()
    except APIException as e:
        return e.to_response()
    else:
        return jsonify(project.model_dump()), 200


@project_bp.route("/<int:project_id>", methods=["DELETE"])
@jwt_required()
def project_delete(project_id: int):
    try:
        delete_project(project_id=project_id)
    except APIException as e:
        return e.to_response()
    else:
        return jsonify(
            {"message": f"Project with id {project_id} has been deleted"}
        ), 200
