import pytest
import pytest_asyncio
from app.core.config import settings  # type: ignore
from app.models.event import Event
from beanie import init_beanie
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError

TEST_DB_NAME = f"{settings.MONGO_DB_NAME}_pytest"


@pytest_asyncio.fixture
async def mongo_db():
    """Beanie binds its client to the running event
    loop, and pytest-asyncio gives each test its own loop.
    """
    client = AsyncMongoClient(settings.MONGO_DB_URL, serverSelectionTimeoutMS=3000)
    try:
        await client.admin.command("ping")
    except PyMongoError as exc:
        await client.close()
        pytest.skip(
            f"MongoDB unavailable ({exc}); start the compose stack to run these"
        )

    database = client.get_database(TEST_DB_NAME)
    await init_beanie(database=database, document_models=[Event])
    await Event.delete_all()

    yield database

    await client.drop_database(TEST_DB_NAME)
    await client.close()


@pytest.fixture
def make_event():
    """Build a valid event payload, overriding only what a test cares about."""

    def _build(**overrides):
        payload = {
            "actor_id": "1",
            "service": "tasks",
            "action": "TASK_CREATE",
            "subject_id": "10",
            "subject_type": "TASK",
            "metadata": {"task_title": "Build API"},
        }
        payload.update(overrides)
        return payload

    return _build
