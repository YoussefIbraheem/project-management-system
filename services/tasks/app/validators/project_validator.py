from utils.exceptions import NotFoundException

from app.models.project import Project


def get_project_or_404(db, project_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException(f"Project with id {project_id} does not exist")
    return project
