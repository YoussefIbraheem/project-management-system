from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.event_service import create_event, get_event_by_id, get_events
from pydantic import ValidationError


@pytest.mark.asyncio
async def test_get_events_builds_query_and_maps_responses():
    class _ComparableField:
        def __init__(self, name: str):
            self.name = name

        def __eq__(self, other):
            return (self.name, "eq", other)

        def __ge__(self, other):
            return (self.name, "ge", other)

        def __neg__(self):
            return self

    class FakeEvent:
        service = _ComparableField("service")
        actor_id = _ComparableField("actor_id")
        timestamp = _ComparableField("timestamp")
        find = MagicMock()

    mock_event = MagicMock()
    mock_event.model_dump.return_value = {
        "_id": "1",
        "actor_id": "1",
        "service": "tasks",
        "action": "created",
        "subject_id": "1",
        "subject_type": "task",
        "metadata": {"key": "value"},
        "timestamp": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }

    mock_query = MagicMock()
    mock_query.sort.return_value.skip.return_value.limit.return_value.to_list = (
        AsyncMock(return_value=[mock_event])
    )
    FakeEvent.find.return_value = mock_query

    with patch("app.services.event_service.Event", new=FakeEvent):
        events = await get_events(
            service="tasks",
            actor_id="1",
            date="2026-01-01",
            limit=10,
            offset=5,
        )

    assert len(events) == 1
    assert events[0].service == "tasks"
    assert events[0].action == "created"
    FakeEvent.find.assert_called_once()
    filters = FakeEvent.find.call_args.args
    assert len(filters) == 3
    assert filters[0] == ("service", "eq", "tasks")
    assert filters[1] == ("actor_id", "eq", "1")
    assert filters[2] == ("timestamp", "ge", datetime(2026, 1, 1, tzinfo=timezone.utc))


@pytest.mark.asyncio
async def test_get_event_by_id_returns_response():
    mock_event = MagicMock()
    mock_event.model_dump.return_value = {
        "_id": "1",
        "actor_id": "1",
        "service": "tasks",
        "action": "created",
        "subject_id": "1",
        "subject_type": "task",
        "metadata": {"key": "value"},
        "timestamp": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }

    with patch("app.services.event_service.Event") as MockEvent:
        MockEvent.get = AsyncMock(return_value=mock_event)
        event = await get_event_by_id("1")

    assert event is not None
    assert event.service == "tasks"
    assert event.id == "1"


@pytest.mark.asyncio
async def test_get_event_by_id_returns_none_for_missing_event():
    with patch("app.services.event_service.Event") as MockEvent:
        MockEvent.get = AsyncMock(return_value=None)
        event = await get_event_by_id("999")

    assert event is None


@pytest.mark.asyncio
async def test_create_event_inserts_and_returns_id():
    with patch("app.services.event_service.Event") as MockEvent:
        mock_instance = MagicMock()
        mock_instance.insert = AsyncMock()
        mock_instance.id = "1"
        MockEvent.return_value = mock_instance

        result = await create_event(
            {
                "actor_id": "1",
                "service": "history",
                "action": "create",
                "subject_id": "1",
                "subject_type": "board",
                "metadata": {"resource": "board"},
            }
        )

    assert result == "1"


@pytest.mark.asyncio
async def test_create_event_rejects_missing_required_fields():
    with pytest.raises(ValidationError):
        await create_event(
            {
                "actor_id": "1",
                "service": "history",
                "action": "create",
                "subject_id": "1",
                "metadata": {"resource": "board"},
            }
        )
