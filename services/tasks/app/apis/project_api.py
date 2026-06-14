from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from utils.openapi.decorators import document

from app.schemas.project_schema import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
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
        {
            "name": "owner_id",
            "type": "string",
            "required": True,
            "description": "The ID of the owner for which to retrieve projects",
        },
        {
            "name": "limit",
            "type": "integer",
            "required": False,
            "description": "The maximum number of projects to retrieve",
        },
        {
            "name": "offset",
            "type": "integer",
            "required": False,
            "description": "The offset for pagination",
        },
    ],
    response_schema=ProjectResponse,
)
@project_bp.route("/", methods=["GET"])
@jwt_required()
def projects_list():
    """
    Retrieve a paginated list of projects filtered by owner.
    """
    try:
        current_user = get_jwt_identity()
        owner_id = request.args.get("owner_id", current_user)
        limit = request.args.get("limit")
        offset = request.args.get("offset")

        projects = get_projects_by_owner(owner_id=owner_id, limit=limit, offset=offset)
        data = [project.model_dump() for project in projects]

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": f"{e}"}), 500


@document(response_schema=ProjectResponse)
@project_bp.route("/<int:project_id>", methods=["GET"])
@jwt_required()
def project_details(project_id: int):
    """
    Retrieve details of a specific project by ID.
    """
    try:
        project = get_project_by_id(project_id=project_id)
        return jsonify(project.model_dump()), 200

    except Exception as e:
        return (
            jsonify({"error": f"Failed to retrieve project: {e}"}),
            500,
        )


@document(
    request_schema=ProjectCreate,
    response_schema=ProjectResponse,
)
@project_bp.route("/", methods=["POST"])
@jwt_required()
def project_create():
    """
    Create a new project with provided data.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data found"}), 400

        data["owner_id"] = get_jwt_identity()
        project_data = ProjectCreate(**data)
        project = create_project(project_data=project_data)
        return jsonify(project.model_dump()), 201
    except Exception as e:
        return (
            jsonify({"error": f"Failed to create project:{str(e)}"}),
            500,
        )


@document(
    request_schema=ProjectUpdate,
    response_schema=ProjectResponse,
)
@project_bp.route("/<int:project_id>", methods=["PUT"])
@jwt_required()
def project_update(project_id: int):
    """
    Update an existing project with new data.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data found"}), 400

        project_data = ProjectUpdate(**data)
        project = update_project(project_id=project_id, project_data=project_data)

        return jsonify(project.model_dump()), 201
    except Exception as e:
        return (
            jsonify({"error": f"Internal Server Error{e}"}),
            500,
        )


@project_bp.route("/<int:project_id>", methods=["DELETE"])
def project_delete(project_id: int):
    """
    Delete a project by ID.
    """
    try:
        delete_project(project_id=project_id)
        return jsonify({"message": "Project Deleted Successfully!"}), 200
    except Exception as e:
        return (
            jsonify({"error": f"Failed to delete project: {str(e)}"}),
            status.HTTP_404_NOT_FOUND,
        )
