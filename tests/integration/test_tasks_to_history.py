import pytest
from conftest import TASKS_URL, auth, eventually, mint_token


@pytest.fixture()
def actor(registered_user):
    return {
        "id": registered_user["id"],
        "token": mint_token(registered_user["id"], is_superuser=True),
    }


@pytest.fixture()
def project(http, actor):
    response = http.post(
        f"{TASKS_URL}/api/v1/projects/",
        headers=auth(actor["token"]),
        json={
            "name": "Integration Project",
            "description": "created by integration suite",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_project_create_lands_in_history(project, actor, history_events):
    def find_event():
        events = history_events(service="tasks", actor_id=actor["id"])
        return next(
            (
                e
                for e in events
                if e["action"] == "PROJECT_CREATE"
                and e["subject_id"] == str(project["id"])
            ),
            None,
        )

    event = eventually(find_event, describe="PROJECT_CREATE event in history")

    assert event["service"] == "tasks"
    assert event["subject_type"] == "PROJECT"


def test_project_update_lands_in_history(http, project, actor, history_events):
    response = http.put(
        f"{TASKS_URL}/api/v1/projects/{project['id']}",
        headers=auth(actor["token"]),
        json={"name": "Integration Project Renamed"},
    )
    assert response.status_code == 200, response.text

    def find_event():
        events = history_events(service="tasks", actor_id=actor["id"])
        return next(
            (
                e
                for e in events
                if e["action"] == "PROJECT_UPDATE"
                and e["subject_id"] == str(project["id"])
            ),
            None,
        )

    event = eventually(find_event, describe="PROJECT_UPDATE event in history")

    assert event["metadata"]["name"] == "Integration Project Renamed"


def test_both_producers_write_to_the_same_history_store(project, actor, history_events):
    """users and tasks publish independently; both must be readable together."""

    def both_present():
        tasks_events = history_events(service="tasks", actor_id=actor["id"])
        users_events = history_events(service="users", actor_id=actor["id"])
        return bool(tasks_events) and bool(users_events)

    eventually(both_present, describe="events from both users and tasks for one actor")
