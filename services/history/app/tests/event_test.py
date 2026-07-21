import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from pydantic import ValidationError

from app.services.event_service import create_event, get_event_by_id, get_events


@pytest.mark.asyncio
async def test_get_events_returns_event_responses():
    mock_event = MagicMock()
    mock_event.model_dump.return_value = {
        "_id": "1",
        "actor_id": "1",
        "service": "test-service",
        "action": "created",
        "subject_id": "1",
        "subject_type": "task",
        "metadata": {"key": "value"},
        "timestamp": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }

    with patch("app.services.event_service.Event") as MockEvent:
        mock_query = MagicMock()
        mock_query.sort.return_value.skip.return_value.limit.return_value.to_list = AsyncMock(return_value=[mock_event])
        MockEvent.find.return_value = mock_query

        events = await get_events(service="test-service")

    assert len(events) == 1
    assert events[0].service == "test-service"
    assert events[0].action == "created"


@pytest.mark.asyncio
async def test_get_event_by_id_returns_response():
    mock_event = MagicMock()
    mock_event.model_dump.return_value = {
        "_id": "1",
        "actor_id": "1",
        "service": "test-service",
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
    assert event.service == "test-service"


@pytest.mark.asyncio
async def test_get_event_by_id_returns_none_for_missing():
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

        result = await create_event({
            "service": "history",
            "action": "create",
            "actor_id": "1",
            "subject_id": "1",
            "subject_type": "board",
            "metadata": {"resource": "board"},
        })

    assert result == "1"


@pytest.mark.asyncio
async def test_create_event_requires_actor_id():
    with pytest.raises(ValidationError):
        await create_event({
            "service": "history",
            "action": "create",
            "subject_id": "1",
            "subject_type": "board",
            "metadata": {"resource": "board"},
        })
