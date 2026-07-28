import httpx
import pytest
from app.main import app
from app.services.event_service import create_event


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _get(path: str, token: str, **params):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://history"
    ) as client:
        return await client.get(path, headers=_auth(token), params=params)


@pytest.mark.asyncio
async def test_list_endpoint_reaches_the_service_layer(
    mongo_db, make_event, superuser_token
):
    """Regression: the route once passed an argument get_events() did not
    accept, so every call returned 500 while the mocked unit test passed."""
    await create_event(make_event())

    response = await _get("/api/v1/events/", superuser_token)

    assert response.status_code == 200, response.text
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_list_endpoint_serialises_every_documented_field(
    mongo_db, make_event, superuser_token
):
    await create_event(make_event())

    response = await _get("/api/v1/events/", superuser_token)

    event = response.json()[0]
    for field in (
        "_id",
        "actor_id",
        "service",
        "action",
        "subject_id",
        "subject_type",
        "metadata",
        "timestamp",
    ):
        assert field in event, f"{field} missing from the API response"


@pytest.mark.asyncio
async def test_list_endpoint_applies_service_filter(
    mongo_db, make_event, superuser_token
):
    await create_event(make_event(service="tasks"))
    await create_event(make_event(service="users", action="USER_REGISTER"))

    response = await _get("/api/v1/events/", superuser_token, service="users")

    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["service"] == "users"


@pytest.mark.asyncio
async def test_list_endpoint_applies_actor_filter(
    mongo_db, make_event, superuser_token
):
    await create_event(make_event(actor_id="1"))
    await create_event(make_event(actor_id="2"))

    response = await _get("/api/v1/events/", superuser_token, actor_id="2")

    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["actor_id"] == "2"


@pytest.mark.asyncio
async def test_list_endpoint_paginates(mongo_db, make_event, superuser_token):
    for i in range(5):
        await create_event(make_event(subject_id=str(i)))

    response = await _get("/api/v1/events/", superuser_token, limit=2, offset=0)

    assert response.status_code == 200, response.text
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_list_endpoint_ignores_unknown_query_params(
    mongo_db, make_event, superuser_token
):
    """The removed `metadata` filter must degrade to an unfiltered read rather
    than erroring, so older clients keep working."""
    await create_event(make_event())

    response = await _get("/api/v1/events/", superuser_token, metadata="anything")

    assert response.status_code == 200, response.text
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_detail_endpoint_returns_the_event(mongo_db, make_event, superuser_token):
    event_id = await create_event(make_event())

    response = await _get(f"/api/v1/events/{event_id}", superuser_token)

    assert response.status_code == 200, response.text
    assert response.json()["_id"] == event_id


@pytest.mark.asyncio
async def test_detail_endpoint_404s_for_unknown_id(mongo_db, superuser_token):
    response = await _get("/api/v1/events/507f1f77bcf86cd799439011", superuser_token)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_endpoints_require_a_token(mongo_db):
    """HTTPBearer answers 401 for a missing header; 403 is reserved for a
    present-but-rejected token (bad scheme, non-superuser)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://history"
    ) as client:
        response = await client.get("/api/v1/events/")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_endpoints_reject_a_non_superuser_token(mongo_db, regular_user_token):
    response = await _get("/api/v1/events/", regular_user_token)

    assert response.status_code == 403
