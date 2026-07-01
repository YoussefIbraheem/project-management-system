from typing import List

from app.db.database import get_db_session
from app.models import ProjectMember
from app.models.project import Project
from app.permissions.project_permission import (
    can_create_project_member,
    can_delete_project,
    can_delete_project_member,
    can_update_project,
    can_update_project_member_role,
)
from app.schemas.project_member_schema import ProjectMemberCreate, ProjectMemberResponse
from app.schemas.project_schema import ProjectCreate, ProjectResponse, ProjectUpdate
from app.security.actor import Actor
from app.security.context import ProjectMemberPermissionContext
from app.security.roles import MemberRole, get_role_object
from app.validators.project_validator import (
    get_member_or_404,
    get_project_or_404,
)


def get_projects(limit: int = 50, offset: int = 0) -> List[ProjectResponse]:
    """Get a list of projects for a specific owner.

    Keyword arguments:
    owner_id -- the ID of the project owner
    limit -- the maximum number of projects to return (default: 50)
    offset -- the number of projects to skip before starting to collect the result set (default: 0)

    Return: a list of ProjectResponse objects representing the projects owned by the specified owner.
    """
    with get_db_session() as db:
        db_projects = db.query(Project).offset(offset).limit(limit).all()

        return [ProjectResponse.model_validate(project) for project in db_projects]


def get_project_by_id(project_id: int) -> ProjectResponse:
    """Get Project Details

    Keyword arguments:
    project_id -- the ID of the project to retrieve
    Return: a ProjectResponse object representing the project with the specified ID, or None if not found
    """
    with get_db_session() as db:
        db_project = get_project_or_404(db, project_id)
        return ProjectResponse.model_validate(db_project)


def create_project(actor: Actor, project_data: ProjectCreate) -> ProjectResponse:
    """Create Project

    Keyword arguments:
    project_data -- the data for the project to be created
    Return: a ProjectResponse object representing the newly created project
    """
    with get_db_session() as db:
        db_project = Project(
            name=project_data.name,
            description=project_data.description,
        )

        owner = ProjectMember(
            project=db_project,
            user_id=actor.user_id,
            role=MemberRole.OWNER.db_value,
        )

        db.add_all([db_project, owner])
        db.commit()

        return ProjectResponse.model_validate(db_project)


def update_project(
    actor: Actor, project_id: int, project_data: ProjectUpdate
) -> ProjectResponse:
    """Update Project

    Keyword arguments:
    project_id -- the ID of the project to update
    project_data -- the updated data for the project
    Return: a ProjectResponse object representing the updated project, or None if not found
    """
    with get_db_session() as db:
        db_project = get_project_or_404(db, project_id)
        member = get_member_or_404(db, project_id, actor.user_id)
        can_update_project(actor, member)

        if project_data.name is not None:
            db_project.name = project_data.name  # type: ignore[assignment]

        if project_data.description is not None:
            db_project.description = project_data.description  # type: ignore[assignment]

        db.commit()
        db.refresh(db_project)

        return ProjectResponse.model_validate(db_project)


def delete_project(actor, project_id: int) -> bool:
    """Delete Project

    Keyword arguments:
    project_id -- the ID of the project to delete
    Return: True if the project was deleted, False otherwise
    """
    with get_db_session() as db:
        db_project = get_project_or_404(db, project_id)
        member = get_member_or_404(db, project_id, actor.user_id)
        can_delete_project(actor, member)

        db.delete(db_project)
        db.commit()
        return True


# Project Member


def get_members(project_id: int):
    """
    Retrieve all members of a project.
    - project_id: The ID of the project.
    - return: A list of ProjectMemberResponse objects representing the members.
    """
    with get_db_session() as db:
        project = get_project_or_404(db, project_id)
        members = db.query(ProjectMember).filter(ProjectMember.project_id == project.id).all()
    
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


def create_member(actor: Actor, project_id: int, member_data: ProjectMemberCreate):
    """
    Create a new member for a project.
    - project_id: The ID of the project.
    - member_data: A ProjectMemberCreate object containing the member's data.
    - return: A ProjectMemberResponse object representing the newly created member.
    """
    with get_db_session() as db:
        action_member = get_member_or_404(db, project_id, actor.user_id)
        target_role = get_role_object(member_data.role)
        ctx = ProjectMemberPermissionContext(
            actor=actor,
            action_member=action_member,
            target_role=target_role,
        )
        can_create_project_member(ctx)

        member = ProjectMember(
            project_id=project_id,
            user_id=member_data.user_id,
            role=member_data.role,
        )
        db.add(member)
        db.flush()
        db.refresh(member)
        return ProjectMemberResponse.model_validate(member)


def update_member_role(actor: Actor, project_id: int, role: str, user_id: str):
    """
    Update the role of a member in a project.
    - project_id: The ID of the project.
    - role_id: The ID of the new role.
    - user_id: The ID of the member to update.
    """
    with get_db_session() as db:
        action_member = get_member_or_404(db, project_id, actor.user_id)
        target_member = get_member_or_404(db, project_id, user_id)
        target_role = get_role_object(role)
        ctx = ProjectMemberPermissionContext(
            actor=actor,
            action_member=action_member,
            target_member=target_member,
            target_role=target_role,
        )
        can_create_project_member(ctx)

        target_member.role = target_role.db_value  # type: ignore[assignment]
        db.flush()
        db.refresh(target_member)

        return ProjectMemberResponse.model_validate(target_member)


def delete_member(actor: Actor, project_id: int, user_id: str):
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
