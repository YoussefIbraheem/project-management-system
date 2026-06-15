from typing import List, Optional

from utils.publisher import publish_history_event
from utils.exceptions import NotFoundException
from app import logger
from app.db.database import get_db_session
from app.events.project_event import ProjectCreatedEvent
from app.models.project import Project
from app.schemas.project_schema import ProjectCreate, ProjectResponse, ProjectUpdate


def get_projects_by_owner(
    owner_id: str, limit: int = 50, offset: int = 0
) -> List[ProjectResponse]:
    """Get a list of projects for a specific owner.

    Keyword arguments:
    owner_id -- the ID of the project owner
    limit -- the maximum number of projects to return (default: 50)
    offset -- the number of projects to skip before starting to collect the result set (default: 0)

    Return: a list of ProjectResponse objects representing the projects owned by the specified owner.
    """
    with get_db_session() as db:
        db_projects = (
            db.query(Project)
            .filter(Project.owner_id == owner_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

        return [ProjectResponse.model_validate(project) for project in db_projects]


def get_project_by_id(project_id: int) -> Optional[ProjectResponse]:
    """Get Project Details

    Keyword arguments:
    project_id -- the ID of the project to retrieve
    Return: a ProjectResponse object representing the project with the specified ID, or None if not found
    """
    with get_db_session() as db:
        db_project = db.query(Project).filter(Project.id == project_id).first()
        if db_project:
            return ProjectResponse.model_validate(db_project)
        raise NotFoundException(f"Project with id {project_id} does not exist")


def create_project(project_data: ProjectCreate) -> ProjectResponse:
    """Create Project

    Keyword arguments:
    project_data -- the data for the project to be created
    Return: a ProjectResponse object representing the newly created project
    """
    with get_db_session() as db:
        db_project = Project(
            name=project_data.name,
            description=project_data.description,
            owner_id=project_data.owner_id,
        )

        db.add(db_project)
        db.flush()
        db.refresh(db_project)

        return ProjectResponse.model_validate(db_project)


def update_project(
    project_id: int, project_data: ProjectUpdate
) -> Optional[ProjectResponse]:
    """Update Project

    Keyword arguments:
    project_id -- the ID of the project to update
    project_data -- the updated data for the project
    Return: a ProjectResponse object representing the updated project, or None if not found
    """
    with get_db_session() as db:
        db_project = db.query(Project).filter(Project.id == project_id).first()

        if not db_project:
            raise NotFoundException(f"Project with id {project_id} does not exist")

        if project_data.name is not None:
            db_project.name = project_data.name

        if project_data.description is not None:
            db_project.description = project_data.description

        db.flush()
        db.refresh(db_project)

        return ProjectResponse.model_validate(db_project)


def delete_project(project_id: int) -> bool:
    """Delete Project

    Keyword arguments:
    project_id -- the ID of the project to delete
    Return: True if the project was deleted, False otherwise
    """
    with get_db_session() as db:
        db_project = db.query(Project).filter(Project.id == project_id).first()

        if db_project:
            db.delete(db_project)
            db.flush()
            return True

        raise NotFoundException(f"Project with id {project_id} does not exist")
