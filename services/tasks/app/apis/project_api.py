from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError
from shared.exceptions import APIException, BadRequestException, ValidationException
from shared.openapi.decorators import document

from app.schemas.project_member_schema import ProjectMemberCreate, ProjectMemberResponse
from app.schemas.project_schema import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import (
    create_member,
    create_project,
    delete_member,
    delete_project,
    get_member_by_id,
    get_members,
    get_project_by_id,
    get_projects,
    update_member_role,
    update_project,
)

from . import get_actor

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
    ],  # type: ignore
    response_schema=ProjectResponse,  # type: ignore
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


@document(response_schema=ProjectResponse)  # type: ignore
@project_bp.route("/<int:project_id>", methods=["GET"])
@jwt_required()
def project_details(project_id: int):
    try:
        project = get_project_by_id(project_id=project_id)
        return jsonify(project.model_dump()), 200
    except APIException as e:
        return e.to_response()


@document(request_schema=ProjectCreate, response_schema=ProjectResponse)  # type: ignore
@project_bp.route("/", methods=["POST"])
@jwt_required()
def project_create():
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")
        project_data = ProjectCreate(**data)
        actor = get_actor()

        project = create_project(actor=actor, project_data=project_data)
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data={err["loc"][0]: err["msg"] for err in e.errors()},
        ).to_response()
    except APIException as e:
        return e.to_response()
    return jsonify(project.model_dump()), 201


@document(request_schema=ProjectUpdate, response_schema=ProjectResponse)  # type: ignore
@project_bp.route("/<int:project_id>", methods=["PUT"])
@jwt_required()
def project_update(project_id: int):
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")
        project_data = ProjectUpdate(**data)
        actor = get_actor()
        project = update_project(
            actor=actor, project_id=project_id, project_data=project_data
        )
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
        actor = get_actor()
        delete_project(actor=actor, project_id=project_id)
    except APIException as e:
        return e.to_response()
    else:
        return jsonify(
            {"message": f"Project with id {project_id} has been deleted"}
        ), 200


@document(response_schema=ProjectMemberResponse)  # type: ignore
@project_bp.route("/<int:project_id>/members", methods=["GET"])
@jwt_required()
def project_members_list(project_id):
    try:
        actor = get_actor()
        members = get_members(actor, project_id)
        return jsonify([member.model_dump() for member in members]), 200
    except APIException as e:
        return e.to_response()


@document(response_schema=ProjectMemberResponse)  # type: ignore
@project_bp.route("/<int:project_id>/members/<int:user_id>", methods=["GET"])
@jwt_required()
def project_member_details(project_id, user_id):
    try:
        actor = get_actor()
        member = get_member_by_id(actor, project_id, str(user_id))
        return jsonify(member.model_dump()), 200
    except APIException as e:
        return e.to_response()


@document(response_schema=ProjectMemberResponse)  # type: ignore
@project_bp.route("/<int:project_id>/members", methods=["POST"])
@jwt_required()
def project_member_create(project_id):
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")
        member_data = ProjectMemberCreate(**data)
        actor = get_actor()
        member = create_member(
            actor=actor, project_id=project_id, member_data=member_data
        )
        return jsonify(member.model_dump()), 201
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data=e.errors(),  # type: ignore
        ).to_response()
    except APIException as e:
        return e.to_response()


@document(response_schema=ProjectMemberResponse)  # type: ignore
@project_bp.route("/<int:project_id>/members/<int:user_id>", methods=["PUT"])
@jwt_required()
def project_member_role_update(project_id, user_id):
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")
        role = data.get("role", None)
        if not role:
            raise BadRequestException("Role is missing in the request data")
        actor = get_actor()
        member = update_member_role(
            actor=actor, project_id=project_id, user_id=user_id, role=role
        )
        return jsonify(member.model_dump()), 200
    except APIException as e:
        return e.to_response()


@project_bp.route("/<int:project_id>/members/<int:user_id>", methods=["DELETE"])
@jwt_required()
def project_member_delete(project_id, user_id):
    try:
        actor = get_actor()
        delete_member(actor=actor, project_id=project_id, user_id=user_id)
        return jsonify({"message": "Member deleted successfully"})
    except APIException as e:
        return e.to_response()
