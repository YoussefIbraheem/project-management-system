from app.db.database import get_db_session
from app.models import MemberRole
from app.schemas.member_role_schema import (
    MemberRoleCreate,
    MemberRoleResponse,
    MemberRoleUpdate,
)
from app.validators.project_validator import (
    ensure_role_is_unique,
    get_role_or_404,
    slugify_role,
)


def get_roles():
    """
    Get all roles from the database.
    - return: List of roles.
    """
    with get_db_session() as db:
        roles = db.query(MemberRole).all()

        return [MemberRoleResponse.model_validate(role) for role in roles]


def get_role(role_id: int):
    """
    Get a specific role by its ID.
    - role_id: The ID of the role to retrieve.
    - return: The role object.
    """
    with get_db_session() as db:
        role = get_role_or_404(db, role_id)

        return MemberRoleResponse.model_validate(role)


def create_role(role_data: MemberRoleCreate):
    """
    Create a new role.
    - label: The label of the role.
    - slug: The slug of the role.
    - Reurn: The created role object.
    """
    with get_db_session() as db:
        role = MemberRole(label=role_data.label, slug=slugify_role(role_data.slug))

        db.add(role)
        db.commit()

        return MemberRoleResponse.model_validate(role)


def update_role(role_id: int, role_data: MemberRoleUpdate):
    """
    Update an existing role.
    - role_id: The ID of the role to update.
    - label: The new label for the role (optional).
    - slug: The new slug for the role (optional).
    - return: The updated role object.
    """
    with get_db_session() as db:
        role = get_role_or_404(db, role_id)
        ensure_role_is_unique(db, role_data.slug)

        if role_data.label is not None:
            role.label = role_data.label #type: ignore

        if role_data.slug is not None:
            role.slug = slugify_role(role_data.slug) #type: ignore

        db.commit()

        return MemberRoleResponse.model_validate(role)


def delete_role(role_id: int):
    with get_db_session() as db:
        role = get_role_or_404(db, role_id)

        db.delete(role)
        db.commit()

        return True
