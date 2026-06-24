import pytest
from app.db.database import get_db_session
from app.models import Project
from app.schemas.project_schema import ProjectCreate, ProjectUpdate
from app.services.project_service import (
    create_project,
    delete_project,
    get_project_by_id,
    get_projects,
    update_project,
)
from utils.exceptions import NotFoundException


def _seed_project(name="Alpha", description="Project Alpha"):
    with get_db_session() as db:
        project = Project(name=name, description=description)
        db.add(project)
        db.flush()
        db.refresh(project)
        return project.id


def test_get_projects_returns_projects():
    first_id = _seed_project()
    second_id = _seed_project("Beta", "Second project")

    projects = get_projects(limit=10, offset=0)

    assert {p.id for p in projects} >= {first_id, second_id}


def test_get_project_by_id_returns_project():
    project_id = _seed_project()

    project = get_project_by_id(project_id) #type: ignore

    assert project.id == project_id
    assert project.name == "Alpha"


def test_create_project_persists_project():
    project = create_project(ProjectCreate(name="Created Project", description="Desc"))

    assert project.id is not None
    assert project.name == "Created Project"
    assert project.description == "Desc"


def test_update_project_updates_fields():
    project_id = _seed_project()

    project = update_project(
        project_id, #type: ignore
        ProjectUpdate(name="Renamed Project", description="Updated desc"),
    )

    assert project.name == "Renamed Project"
    assert project.description == "Updated desc"


def test_delete_project_returns_true():
    project_id = _seed_project()

    assert delete_project(project_id) is True #type: ignore


def test_get_project_by_id_raises_not_found():
    with pytest.raises(NotFoundException):
        get_project_by_id(999)
