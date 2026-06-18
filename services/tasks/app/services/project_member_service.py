from utils.exceptions import NotFoundException

from app.db.database import get_db_session
from app.models import MemberRole, ProjectMember
from app.schemas.project_member_schema import ProjectMemberCreate, ProjectMemberResponse

from .project_service import get_project_by_id


def get_members(project_id: int):
    with get_db_session() as db:
        project = get_project_by_id(project_id)
        print(project)
        if not project:
            raise NotFoundException(f"Project with id {project_id} does not exist")

        members = (
            db.query(ProjectMember).filter(ProjectMember.project_id == project.id).all()
        )
        return [ProjectMemberResponse.model_validate(member) for member in members]


def get_member(project_id: int, user_id: str):
    with get_db_session() as db:
        member = (
            db.query(ProjectMember)
            .filter_by(project_id=project_id, user_id=user_id)
            .first()
        )
        if not member:
            raise NotFoundException(
                f"User with id {user_id} does not exist in project with id {project_id}"
            )

        return ProjectMemberResponse.model_validate(member)


def create_member(project_id: int, member_data: ProjectMemberCreate):
    with get_db_session() as db:
        project = get_project_by_id(project_id)
        if not project:
            raise NotFoundException(f"Project with id {project_id} does not exist")

        member = ProjectMember(
            project_id=project_id,
            user_id=member_data.user_id,
            role_id=member_data.role_id,
        )
        db.add(member)
        db.flush()
        db.refresh(member)
        return ProjectMemberResponse.model_validate(member)


def update_member_role(project_id: int, role_id: int, user_id: str):
    with get_db_session() as db:
        member = get_member(project_id, user_id)

        if not member:
            raise NotFoundException(
                f"User with id {user_id} does not exist in project with id {project_id}"
            )

        role = db.query(MemberRole).filter_by(id=role_id).first()

        if not role:
            raise NotFoundException(f"Role with id {role_id} does not exist")

        member.role_id = role_id
        db.flush()
        db.refresh(member)

        return ProjectMemberResponse.model_validate(member)


def delete_member(project_id: int, user_id: str):
    with get_db_session() as db:
        project = get_project_by_id(project_id)
        if not project:
            raise NotFoundException(f"Project with id {project_id} does not exist")

        member = (
            db.query(ProjectMember)
            .filter_by(project_id=project.id, user_id=user_id)
            .first()
        )
        if not member:
            raise NotFoundException(
                f"User with id {user_id} does not exist in project with id {project_id}"
            )

        db.delete(member)
        db.flush()
        return True
