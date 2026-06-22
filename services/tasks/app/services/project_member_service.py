from app.db.database import get_db_session
from app.models import ProjectMember
from app.schemas.project_member_schema import ProjectMemberCreate, ProjectMemberResponse
from app.validators.project_member_validator import get_member_or_404, get_role_or_404
from app.validators.project_validator import get_project_or_404


def get_members(project_id: int):
    with get_db_session() as db:
        project = get_project_or_404(db, project_id)
        members = (
            db.query(ProjectMember).filter(ProjectMember.project_id == project.id).all()
        )
        return [ProjectMemberResponse.model_validate(member) for member in members]


def get_member(project_id: int, user_id: str):
    with get_db_session() as db:
        member = get_member_or_404(db, project_id, user_id)
        return ProjectMemberResponse.model_validate(member)


def create_member(project_id: int, member_data: ProjectMemberCreate):
    with get_db_session() as db:
        get_project_or_404(db, project_id)
        get_role_or_404(db, role_id)

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
        member = get_member_or_404(db, project_id, user_id)
        get_role_or_404(db, role_id)

        member.role_id = role_id  # type: ignore[assignment]
        db.flush()
        db.refresh(member)

        return ProjectMemberResponse.model_validate(member)


def delete_member(project_id: int, user_id: str):
    with get_db_session() as db:
        member = get_member_or_404(db, project_id, user_id)

        db.delete(member)
        db.flush()
        return True
