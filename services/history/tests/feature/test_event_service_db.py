from datetime import datetime, timedelta, timezone

import pytest
from app.models.event import Event
from app.services.event_service import create_event, get_event_by_id, get_events
from pydantic import ValidationError


@pytest.mark.asyncio
async def test_create_event_persists_all_fields(mongo_db, make_event):
    payload = make_event()

    event_id = await create_event(payload)

    stored = await Event.get(event_id)
    assert stored is not None
    assert stored.actor_id == payload["actor_id"]
    assert stored.service == payload["service"]
    assert stored.action == payload["action"]
    assert stored.subject_id == payload["subject_id"]
    assert stored.subject_type == payload["subject_type"]
    assert stored.metadata == payload["metadata"]


@pytest.mark.asyncio
async def test_create_event_stamps_timestamp_in_utc(mongo_db, make_event):
    before = datetime.now(timezone.utc)

    event_id = await create_event(make_event())

    stored = await Event.get(event_id)
    if stored:
        assert stored.timestamp.tzinfo is not None, "timestamp must be timezone-aware"
        assert stored.timestamp >= before - timedelta(seconds=5)


@pytest.mark.asyncio
async def test_create_event_rejects_incomplete_payload(mongo_db, make_event):
    payload = make_event()
    del payload["actor_id"]

    with pytest.raises(ValidationError):
        await create_event(payload)

    assert await Event.find_all().count() == 0


@pytest.mark.asyncio
async def test_get_events_returns_everything_when_unfiltered(mongo_db, make_event):
    for i in range(3):
        await create_event(make_event(subject_id=str(i)))

    events = await get_events()

    assert len(events) == 3


@pytest.mark.asyncio
async def test_get_events_filters_by_service(mongo_db, make_event):
    await create_event(make_event(service="tasks"))
    await create_event(make_event(service="users", action="USER_REGISTER"))

    events = await get_events(service="users")

    assert len(events) == 1
    assert events[0].service == "users"


@pytest.mark.asyncio
async def test_get_events_filters_by_actor(mongo_db, make_event):
    await create_event(make_event(actor_id="1"))
    await create_event(make_event(actor_id="2"))

    events = await get_events(actor_id="2")

    assert len(events) == 1
    assert events[0].actor_id == "2"


@pytest.mark.asyncio
async def test_get_events_combines_service_and_actor_filters(mongo_db, make_event):
    await create_event(make_event(service="tasks", actor_id="1"))
    await create_event(make_event(service="tasks", actor_id="2"))
    await create_event(make_event(service="users", actor_id="1"))

    events = await get_events(service="tasks", actor_id="1")

    assert len(events) == 1
    assert events[0].service == "tasks"
    assert events[0].actor_id == "1"


@pytest.mark.asyncio
async def test_get_events_returns_newest_first(mongo_db, make_event):
    for i in range(3):
        await create_event(make_event(subject_id=str(i)))

    events = await get_events()

    timestamps = [e.timestamp for e in events]
    assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.asyncio
async def test_get_events_honours_limit_and_offset(mongo_db, make_event):
    for i in range(5):
        await create_event(make_event(subject_id=str(i)))

    first_page = await get_events(limit=2)
    second_page = await get_events(limit=2, offset=2)

    assert len(first_page) == 2
    assert len(second_page) == 2
    assert {e.id for e in first_page}.isdisjoint({e.id for e in second_page})


@pytest.mark.asyncio
async def test_get_events_filters_by_date_floor(mongo_db, make_event):
    await create_event(make_event())
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")

    assert await get_events(date="1970-01-01") != []
    assert await get_events(date=tomorrow) == []


@pytest.mark.asyncio
async def test_get_event_by_id_returns_the_event(mongo_db, make_event):
    event_id = await create_event(make_event())

    event = await get_event_by_id(event_id)

    assert event is not None
    assert str(event.id) == event_id


@pytest.mark.asyncio
async def test_get_event_by_id_returns_none_when_absent(mongo_db):
    assert await get_event_by_id("507f1f77bcf86cd799439011") is None
