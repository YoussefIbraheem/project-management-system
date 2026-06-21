from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError
from utils.exceptions import APIException, BadRequestException, ValidationException
from utils.openapi.decorators import document

from app.schemas.project_member_schema import ProjectMemberCreate, ProjectMemberResponse
from app.services.project_member_service import (
    create_member,
    delete_member,
    get_member,
    get_members,
    update_member_role,
)

project_member_bp = Blueprint("project_member", __name__, url_prefix="/api/v1/projects")


@document(response_schema=ProjectMemberResponse)
@project_member_bp.route("/<int:project_id>/members", methods=["GET"])
@jwt_required()
def project_members_list(project_id):
    try:
        members = get_members(project_id)
        return jsonify(members)
    except APIException as e:
        return e.to_response()


@document(response_schema=ProjectMemberResponse)
@project_member_bp.route("/<int:project_id>/members/<int:user_id>", methods=["GET"])
@jwt_required()
def project_member_details(project_id, user_id):
    try:
        member = get_member(project_id, user_id)
        return jsonify(member)
    except APIException as e:
        return e.to_response()


@document(response_schema=ProjectMemberResponse)
@project_member_bp.route("/<int:project_id>/members", methods=["POST"])
@jwt_required()
def project_member_create(project_id):
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")
        project_member_data = ProjectMemberCreate(**data)
        member = create_member(project_id, project_member_data)
        return jsonify(member)
    except ValidationError as e:
        return ValidationException(
            message="Validation Error", data=e.errors()
        ).to_response()
    except APIException as e:
        return e.to_response()


@document(response_schema=ProjectMemberResponse)
@project_member_bp.route("/<int:project_id>/members/<int:user_id>", methods=["PUT"])
@jwt_required()
def project_member_role_update(project_id, user_id):
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")
        role_id = data.get("role_id", None)
        if not role_id:
            raise BadRequestException("Role ID is missing in the request data")

        member = update_member_role(
            project_id=project_id, user_id=user_id, role_id=role_id
        )
        return jsonify(member)
    except APIException as e:
        return e.to_response()


@project_member_bp.route("/<int:project_id>/members/<int:user_id>", methods=["DELETE"])
@jwt_required()
def project_member_delete(project_id, user_id):
    try:
        delete_member(project_id, user_id)
        return jsonify({"message": "Member deleted successfully"})
    except APIException as e:
        return e.to_response()
