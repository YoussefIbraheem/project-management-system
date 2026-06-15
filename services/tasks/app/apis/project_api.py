from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from utils.exceptions import APIException, BadRequestException, ValidationException
from utils.openapi.decorators import document
from app.schemas.project_schema import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import (
    create_project,
    delete_project,
    get_project_by_id,
    get_projects_by_owner,
    update_project,
)

project_bp = Blueprint("project", __name__, url_prefix="/api/v1/projects")


@document(
    query_params=[
        {"name": "owner_id", "type": "string",  "required": True,  "description": "Owner ID to filter projects"},
        {"name": "limit",    "type": "integer", "required": False, "description": "Max number of projects to retrieve"},
        {"name": "offset",   "type": "integer", "required": False, "description": "Pagination offset"},
    ],
    response_schema=ProjectResponse,
)
@project_bp.route("/", methods=["GET"])
@jwt_required()
def projects_list():
    """Retrieve a paginated list of projects filtered by owner."""
    try:
        current_user = get_jwt_identity()
        owner_id = request.args.get("owner_id", current_user)
        limit = request.args.get("limit")
        offset = request.args.get("offset")
        projects = get_projects_by_owner(owner_id=owner_id, limit=limit, offset=offset)
        return jsonify([p.model_dump() for p in projects]), 200
    except APIException as e:
        return e.to_response()


@document(response_schema=ProjectResponse)
@project_bp.route("/<int:project_id>", methods=["GET"])
@jwt_required()
def project_details(project_id: int):
    """Retrieve details of a specific project by ID."""
    try:
        project = get_project_by_id(project_id=project_id)
        return jsonify(project.model_dump()), 200
    except APIException as e:
        return e.to_response()


@document(request_schema=ProjectCreate, response_schema=ProjectResponse)
@project_bp.route("/", methods=["POST"])
@jwt_required()
def project_create():
    """Create a new project with provided data."""
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")
        data["owner_id"] = get_jwt_identity()
        project_data = ProjectCreate(**data)
        project = create_project(project_data=project_data)
        return jsonify(project.model_dump()), 201
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data={err["loc"][0]: err["msg"] for err in e.errors()},
        ).to_response()
    except APIException as e:
        return e.to_response()


@document(request_schema=ProjectUpdate, response_schema=ProjectResponse)
@project_bp.route("/<int:project_id>", methods=["PUT"])
@jwt_required()
def project_update(project_id: int):
    """Update an existing project with new data."""
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")
        project_data = ProjectUpdate(**data)
        project = update_project(project_id=project_id, project_data=project_data)
        return jsonify(project.model_dump()), 200  # 200 not 201
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data={err["loc"][0]: err["msg"] for err in e.errors()},
        ).to_response()
    except APIException as e:
        return e.to_response()


@project_bp.route("/<int:project_id>", methods=["DELETE"])
@jwt_required()  # was missing
def project_delete(project_id: int):
    """Delete a project by ID."""
    try:
        delete_project(project_id=project_id)
        return jsonify({"message": "Project deleted successfully"}), 200
    except APIException as e:
        return e.to_response()