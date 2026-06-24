from app.db.database import get_db_session
from app.models import ProjectMember
from app.schemas.project_member_schema import ProjectMemberCreate, ProjectMemberResponse
from app.validators.project_validator import (
    get_member_or_404,
    get_project_or_404,
    get_role_or_404,
)


def get_members(project_id: int):
    """
    Retrieve all members of a project.
    - project_id: The ID of the project.
    - return: A list of ProjectMemberResponse objects representing the members.
    """
    with get_db_session() as db:
        project = get_project_or_404(db, project_id)
        members = (
            db.query(ProjectMember).filter(ProjectMember.project_id == project.id).all()
        )
        return [ProjectMemberResponse.model_validate(member) for member in members]


def get_member(project_id: int, user_id: str):
    """
    Retrieve a specific member of a project by their user ID.
    - project_id: The ID of the project.
    - user_id: The user ID of the member.
    - return: A ProjectMemberResponse object representing the member.
    """
    with get_db_session() as db:
        member = get_member_or_404(db, project_id, user_id)
        return ProjectMemberResponse.model_validate(member)


def create_member(project_id: int, member_data: ProjectMemberCreate):
    """
    Create a new member for a project.
    - project_id: The ID of the project.
    - member_data: A ProjectMemberCreate object containing the member's data.
    - return: A ProjectMemberResponse object representing the newly created member.
    """
    with get_db_session() as db:
        project = get_project_or_404(db, project_id)
        role = get_role_or_404(db, member_data.role_id)

        member = ProjectMember(
            project_id=project.id,
            user_id=member_data.user_id,
            role_id=role.id,
        )
        db.add(member)
        db.flush()
        db.refresh(member)
        return ProjectMemberResponse.model_validate(member)


def update_member_role(project_id: int, role_id: int, user_id: str):
    """
    Update the role of a member in a project.
    - project_id: The ID of the project.
    - role_id: The ID of the new role.
    - user_id: The ID of the member to update.
    """
    with get_db_session() as db:
        member = get_member_or_404(db, project_id, user_id)
        get_role_or_404(db, role_id)

        member.role_id = role_id  # type: ignore[assignment]
        db.flush()
        db.refresh(member)

        return ProjectMemberResponse.model_validate(member)


def delete_member(project_id: int, user_id: str):
    """
    Delete a member from a project.
    - project_id: The ID of the project.
    - user_id: The ID of the member to delete.
    - return: A boolean indicating whether the deletion was successful.
    """
    with get_db_session() as db:
        member = get_member_or_404(db, project_id, user_id)

        db.delete(member)
        db.flush()
        return True
