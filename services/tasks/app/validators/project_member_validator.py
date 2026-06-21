from utils.exceptions import NotFoundException

from app.models import MemberRole, ProjectMember


def get_member_or_404(db, project_id: int, user_id: str) -> ProjectMember:
    member = (
        db.query(ProjectMember)
        .filter_by(project_id=project_id, user_id=user_id)
        .first()
    )
    if not member:
        raise NotFoundException(
            f"User with id {user_id} does not exist in project with id {project_id}"
        )
    return member


def get_role_or_404(db, role_id: int) -> MemberRole:
    role = db.query(MemberRole).filter_by(id=role_id).first()
    if not role:
        raise NotFoundException(f"Role with id {role_id} does not exist")
    return role
