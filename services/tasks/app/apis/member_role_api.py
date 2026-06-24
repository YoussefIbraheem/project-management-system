from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from pydantic import ValidationError
from utils.exceptions import APIException, BadRequestException, ValidationException
from utils.openapi.decorators import document

from app.schemas.member_role_schema import (
    MemberRoleCreate,
    MemberRoleResponse,
    MemberRoleUpdate,
)
from app.services.member_role_service import (
    create_role,
    delete_role,
    get_role,
    get_roles,
    update_role,
)

member_role_bp = Blueprint("member_role", __name__, url_prefix="/api/v1/roles")


@document(response_schema=MemberRoleResponse)  # type: ignore[assignments]
@jwt_required()
@member_role_bp.route("/", methods=["GET"])
def roles_get():
    try:
        return jsonify([role.model_dump() for role in get_roles()]), 200
    except APIException as e:
        return e.to_response()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@document(response_schema=MemberRoleResponse)  # type: ignore[assignments]
@jwt_required()
@member_role_bp.route("/<int:role_id>", methods=["GET"])
def role_get(role_id):
    try:
        role = get_role(role_id)
        return jsonify(role.model_dump()), 200
    except APIException as e:
        return e.to_response()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@document(response_schema=MemberRoleResponse)  # type: ignore[assignments]
@jwt_required()
@member_role_bp.route("/", methods=["POST"])
def role_create():
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")
        role_data = MemberRoleCreate(**data)
        new_role = create_role(role_data)
        return jsonify(new_role.model_dump()), 201
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data={err["loc"][0]: err["msg"] for err in e.errors()},
        ).to_response()
    except APIException as e:
        return e.to_response()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@document(response_schema=MemberRoleResponse)  # type: ignore[assignments]
@jwt_required()
@member_role_bp.route("/<int:role_id>", methods=["PUT"])
def role_update(role_id: int):
    try:
        data = request.get_json()
        if not data:
            raise BadRequestException("Request body is missing or not valid JSON")
        role_data = MemberRoleUpdate(**data)
        updated_role = update_role(role_id, role_data)
        return jsonify(updated_role.model_dump()), 200
    except ValidationError as e:
        return ValidationException(
            message="Validation Error",
            data={err["loc"][0]: err["msg"] for err in e.errors()},
        ).to_response()
    except APIException as e:
        return e.to_response()


@jwt_required()
@member_role_bp.route("/<int:role_id>", methods=["DELETE"])
def role_delete(role_id):
    try:
        delete_role(role_id)
        return jsonify({"message": "Role deleted successfully"}), 200
    except APIException as e:
        return e.to_response()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
