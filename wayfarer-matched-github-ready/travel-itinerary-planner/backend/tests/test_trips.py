import os
import uuid

import pytest
from fastapi.testclient import TestClient

# Force memory store before importing the app modules that read env.
os.environ["WANDERPLAN_TRIP_STORE"] = "memory"

from main import app  # noqa: E402
from services.trips import _memory_store  # noqa: E402


@pytest.fixture(autouse=True)
def reset_memory_store():
    _memory_store._rows.clear()
    yield
    _memory_store._rows.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def owner_headers():
    return {"X-WanderPlan-Owner-Key": str(uuid.uuid4())}


def _sample_preferences():
    return {
        "destination": "Goa, India",
        "start_date": "2026-11-01",
        "end_date": "2026-11-03",
        "budget_inr": 30000,
        "travel_style": "balanced",
        "interests": ["food", "nature"],
    }


def _generate(client: TestClient, preferences: dict):
    response = client.post("/api/itineraries/generate", json=preferences)
    assert response.status_code == 200, response.text
    return response.json()


def test_health_still_works(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "supabase" in body


def test_generate_still_works(client):
    itinerary = _generate(client, _sample_preferences())
    assert itinerary["generator"] == "rule_based_demo"
    assert itinerary["trip_days"] == 3


def test_save_list_get_update_delete_trip(client, owner_headers):
    preferences = _sample_preferences()
    itinerary = _generate(client, preferences)

    save_resp = client.post(
        "/api/trips",
        headers=owner_headers,
        json={"preferences": preferences, "itinerary": itinerary},
    )
    assert save_resp.status_code == 201, save_resp.text
    saved = save_resp.json()
    trip_id = saved["id"]
    assert saved["destination"] == "Goa, India"
    assert "preferences" in saved and "itinerary" in saved

    list_resp = client.get("/api/trips", headers=owner_headers)
    assert list_resp.status_code == 200
    listed = list_resp.json()
    assert listed["count"] == 1
    assert listed["trips"][0]["id"] == trip_id

    get_resp = client.get(f"/api/trips/{trip_id}", headers=owner_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["itinerary"]["trip_days"] == 3

    patch_resp = client.patch(
        f"/api/trips/{trip_id}",
        headers=owner_headers,
        json={"title": "Goa weekend"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["title"] == "Goa weekend"

    delete_resp = client.delete(f"/api/trips/{trip_id}", headers=owner_headers)
    assert delete_resp.status_code == 204

    missing = client.get(f"/api/trips/{trip_id}", headers=owner_headers)
    assert missing.status_code == 404


def test_owner_isolation(client, owner_headers):
    preferences = _sample_preferences()
    itinerary = _generate(client, preferences)
    save_resp = client.post(
        "/api/trips",
        headers=owner_headers,
        json={"preferences": preferences, "itinerary": itinerary},
    )
    trip_id = save_resp.json()["id"]

    other = {"X-WanderPlan-Owner-Key": str(uuid.uuid4())}
    assert client.get("/api/trips", headers=other).json()["count"] == 0
    assert client.get(f"/api/trips/{trip_id}", headers=other).status_code == 404


def test_save_requires_owner_key(client):
    preferences = _sample_preferences()
    itinerary = _generate(client, preferences)
    response = client.post(
        "/api/trips",
        json={"preferences": preferences, "itinerary": itinerary},
    )
    assert response.status_code == 400


def test_save_rejects_mismatched_destination(client, owner_headers):
    preferences = _sample_preferences()
    itinerary = _generate(client, preferences)
    itinerary["destination"] = "Somewhere Else"
    response = client.post(
        "/api/trips",
        headers=owner_headers,
        json={"preferences": preferences, "itinerary": itinerary},
    )
    assert response.status_code == 422
