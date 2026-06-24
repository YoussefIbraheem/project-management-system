from utils.exceptions import BadRequestException, NotFoundException
from app.models import MemberRole, Project, ProjectMember
from slugify import slugify


def get_project_or_404(db, project_id: int) -> Project:
    """
    Retrieve a project by its ID or raise a 404 error if the project is not found.
    - db: SQLAlchemy database session.
    - project_id: ID of the project to retrieve.
    - return: Project object.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException(f"Project with id {project_id} does not exist")
    return project


def get_member_or_404(db, project_id: int, user_id: str) -> ProjectMember:
    """
    Retrieve a project member by their ID or raise a 404 error if the member is not found.
    - db: SQLAlchemy database session.
    - project_id: ID of the project to retrieve.
    - user_id: ID of the user to retrieve.
    - return:
    """
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
    """
    Retrieve a role by its ID or raise a 404 error if the role is not found.
    - db: SQLAlchemy database session.
    - role_id: ID of the role to retrieve.
    - return:
    """
    role = db.query(MemberRole).filter_by(id=role_id).first()
    if not role:
        raise NotFoundException(f"Role with id {role_id} does not exist")
    return role

def ensure_role_is_unique(db,slug:str):
    """
    Ensure that a role slug is unique.
    - db: SQLAlchemy database session.
    - slug: Slug of the role to check.
    - return:
    """
    existing_role = db.query(MemberRole).filter_by(slug=slug).first()
    if existing_role:
        raise BadRequestException(f"Role slug '{slug}' is already taken")


def slugify_role(input: str) -> str:
    """
    Convert a role name to a slug.
    - name: Name of the role to convert.
    - return:
    """
    return slugify(input)


def ensure_member_in_project(db, project_id, user_id):
    """
    Ensure that a user is a member of a project.
    - db: SQLAlchemy database session.
    - project_id: ID of the project to check.
    - user_id: ID of the user to check.
    - return:
    """
    member = get_member_or_404(db, project_id, user_id)
    if not member:
        raise NotFoundException(
            f"User with id {user_id} does not exist in project with id {project_id}"
        )
    return member
