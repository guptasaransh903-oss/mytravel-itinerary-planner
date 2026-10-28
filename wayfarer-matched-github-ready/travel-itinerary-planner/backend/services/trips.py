"""
Saved-trip persistence.

Primary store: Supabase table public.saved_trips via the service-role key
(so RLS can stay enabled for anon/authenticated clients).

Optional memory store: set WANDERPLAN_TRIP_STORE=memory for local tests without
Supabase. Not used for durable production data.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Protocol

from models.schemas import (
    ItineraryRequest,
    ItineraryResponse,
    SavedTrip,
    SavedTripSummary,
    SaveTripRequest,
    TravelStyle,
    UpdateTripRequest,
)
from db.supabase_client import get_supabase_client, get_supabase_config

TABLE_NAME = "saved_trips"
OWNER_KEY_HEADER = "X-WanderPlan-Owner-Key"
OWNER_KEY_MIN_LEN = 32


class TripStoreError(Exception):
    """Base error for trip persistence."""


class TripStoreUnavailable(TripStoreError):
    """Supabase persistence is not configured or unreachable."""


class TripNotFound(TripStoreError):
    """Requested trip does not exist for this owner."""


class TripStore(Protocol):
    def create(self, owner_key: str, payload: SaveTripRequest) -> SavedTrip: ...

    def list(self, owner_key: str) -> list[SavedTripSummary]: ...

    def get(self, owner_key: str, trip_id: str) -> SavedTrip: ...

    def update(
        self, owner_key: str, trip_id: str, payload: UpdateTripRequest
    ) -> SavedTrip: ...

    def delete(self, owner_key: str, trip_id: str) -> None: ...


def validate_owner_key(owner_key: str | None) -> str:
    key = (owner_key or "").strip()
    if len(key) < OWNER_KEY_MIN_LEN:
        raise ValueError(
            f"Missing or invalid {OWNER_KEY_HEADER}. "
            "Send a stable client-generated UUID (at least 32 characters)."
        )
    return key


def _default_title(destination: str, start_date: Any, end_date: Any) -> str:
    return f"{destination} ({start_date} to {end_date})"


def _iso(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _row_to_summary(row: dict[str, Any]) -> SavedTripSummary:
    interests = row.get("interests") or []
    if isinstance(interests, str):
        interests = []
    return SavedTripSummary(
        id=str(row["id"]),
        title=row.get("title") or _default_title(
            row["destination"], row["start_date"], row["end_date"]
        ),
        destination=row["destination"],
        start_date=row["start_date"],
        end_date=row["end_date"],
        budget_inr=int(row["budget_inr"]),
        travel_style=TravelStyle(row["travel_style"]),
        interests=list(interests),
        total_estimated_cost_inr=int(row.get("total_estimated_cost_inr") or 0),
        trip_days=int(row.get("trip_days") or 1),
        created_at=_iso(row.get("created_at")),
        updated_at=_iso(row.get("updated_at")),
    )


def _row_to_trip(row: dict[str, Any]) -> SavedTrip:
    summary = _row_to_summary(row)
    preferences_raw = row.get("preferences") or {}
    itinerary_raw = row.get("itinerary") or {}
    return SavedTrip(
        **summary.model_dump(),
        preferences=ItineraryRequest.model_validate(preferences_raw),
        itinerary=ItineraryResponse.model_validate(itinerary_raw),
    )


def _build_insert_row(owner_key: str, payload: SaveTripRequest) -> dict[str, Any]:
    pref = payload.preferences
    itin = payload.itinerary
    title = (payload.title or "").strip() or _default_title(
        pref.destination, pref.start_date, pref.end_date
    )
    return {
        "owner_key": owner_key,
        "destination": pref.destination,
        "start_date": pref.start_date.isoformat(),
        "end_date": pref.end_date.isoformat(),
        "budget_inr": pref.budget_inr,
        "travel_style": pref.travel_style.value,
        "interests": list(pref.interests),
        "preferences": pref.model_dump(mode="json"),
        "itinerary": itin.model_dump(mode="json"),
        "total_estimated_cost_inr": itin.total_estimated_cost_inr,
        "trip_days": itin.trip_days,
        "title": title,
    }


class MemoryTripStore:
    """Process-local store for tests / optional local mode."""

    def __init__(self) -> None:
        self._rows: dict[str, dict[str, Any]] = {}
        self._lock = Lock()

    def create(self, owner_key: str, payload: SaveTripRequest) -> SavedTrip:
        row = _build_insert_row(owner_key, payload)
        now = datetime.now(timezone.utc).isoformat()
        trip_id = str(uuid.uuid4())
        row.update({"id": trip_id, "created_at": now, "updated_at": now})
        with self._lock:
            self._rows[trip_id] = row
        return _row_to_trip(row)

    def list(self, owner_key: str) -> list[SavedTripSummary]:
        with self._lock:
            rows = [r for r in self._rows.values() if r["owner_key"] == owner_key]
        rows.sort(key=lambda r: r["created_at"], reverse=True)
        return [_row_to_summary(r) for r in rows]

    def get(self, owner_key: str, trip_id: str) -> SavedTrip:
        with self._lock:
            row = self._rows.get(trip_id)
        if not row or row["owner_key"] != owner_key:
            raise TripNotFound("Trip not found")
        return _row_to_trip(row)

    def update(
        self, owner_key: str, trip_id: str, payload: UpdateTripRequest
    ) -> SavedTrip:
        with self._lock:
            row = self._rows.get(trip_id)
            if not row or row["owner_key"] != owner_key:
                raise TripNotFound("Trip not found")
            if payload.title is not None:
                row["title"] = payload.title.strip()
            if payload.preferences is not None:
                pref = payload.preferences
                row["destination"] = pref.destination
                row["start_date"] = pref.start_date.isoformat()
                row["end_date"] = pref.end_date.isoformat()
                row["budget_inr"] = pref.budget_inr
                row["travel_style"] = pref.travel_style.value
                row["interests"] = list(pref.interests)
                row["preferences"] = pref.model_dump(mode="json")
            if payload.itinerary is not None:
                itin = payload.itinerary
                row["itinerary"] = itin.model_dump(mode="json")
                row["total_estimated_cost_inr"] = itin.total_estimated_cost_inr
                row["trip_days"] = itin.trip_days
                row["destination"] = itin.destination
                row["start_date"] = itin.start_date.isoformat()
                row["end_date"] = itin.end_date.isoformat()
                row["travel_style"] = itin.travel_style.value
                row["interests"] = list(itin.interests)
                row["budget_inr"] = itin.budget_inr
            row["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._rows[trip_id] = row
            return _row_to_trip(row)

    def delete(self, owner_key: str, trip_id: str) -> None:
        with self._lock:
            row = self._rows.get(trip_id)
            if not row or row["owner_key"] != owner_key:
                raise TripNotFound("Trip not found")
            del self._rows[trip_id]


class SupabaseTripStore:
    def __init__(self, client: Any) -> None:
        self._client = client

    def create(self, owner_key: str, payload: SaveTripRequest) -> SavedTrip:
        row = _build_insert_row(owner_key, payload)
        try:
            result = self._client.table(TABLE_NAME).insert(row).execute()
        except Exception as exc:  # noqa: BLE001
            raise TripStoreUnavailable(_friendly_db_error(exc)) from exc
        data = _first_row(result)
        if not data:
            raise TripStoreUnavailable("Insert succeeded but no row was returned")
        return _row_to_trip(data)

    def list(self, owner_key: str) -> list[SavedTripSummary]:
        try:
            result = (
                self._client.table(TABLE_NAME)
                .select(
                    "id,title,destination,start_date,end_date,budget_inr,"
                    "travel_style,interests,total_estimated_cost_inr,trip_days,"
                    "created_at,updated_at"
                )
                .eq("owner_key", owner_key)
                .order("created_at", desc=True)
                .execute()
            )
        except Exception as exc:  # noqa: BLE001
            raise TripStoreUnavailable(_friendly_db_error(exc)) from exc
        rows = result.data or []
        return [_row_to_summary(row) for row in rows]

    def get(self, owner_key: str, trip_id: str) -> SavedTrip:
        try:
            result = (
                self._client.table(TABLE_NAME)
                .select("*")
                .eq("owner_key", owner_key)
                .eq("id", trip_id)
                .limit(1)
                .execute()
            )
        except Exception as exc:  # noqa: BLE001
            raise TripStoreUnavailable(_friendly_db_error(exc)) from exc
        rows = result.data or []
        if not rows:
            raise TripNotFound("Trip not found")
        return _row_to_trip(rows[0])

    def update(
        self, owner_key: str, trip_id: str, payload: UpdateTripRequest
    ) -> SavedTrip:
        updates: dict[str, Any] = {}
        if payload.title is not None:
            updates["title"] = payload.title.strip()
        if payload.preferences is not None:
            pref = payload.preferences
            updates.update(
                {
                    "destination": pref.destination,
                    "start_date": pref.start_date.isoformat(),
                    "end_date": pref.end_date.isoformat(),
                    "budget_inr": pref.budget_inr,
                    "travel_style": pref.travel_style.value,
                    "interests": list(pref.interests),
                    "preferences": pref.model_dump(mode="json"),
                }
            )
        if payload.itinerary is not None:
            itin = payload.itinerary
            updates.update(
                {
                    "itinerary": itin.model_dump(mode="json"),
                    "total_estimated_cost_inr": itin.total_estimated_cost_inr,
                    "trip_days": itin.trip_days,
                    "destination": itin.destination,
                    "start_date": itin.start_date.isoformat(),
                    "end_date": itin.end_date.isoformat(),
                    "travel_style": itin.travel_style.value,
                    "interests": list(itin.interests),
                    "budget_inr": itin.budget_inr,
                }
            )
        try:
            result = (
                self._client.table(TABLE_NAME)
                .update(updates)
                .eq("owner_key", owner_key)
                .eq("id", trip_id)
                .execute()
            )
        except Exception as exc:  # noqa: BLE001
            raise TripStoreUnavailable(_friendly_db_error(exc)) from exc
        rows = result.data or []
        if not rows:
            raise TripNotFound("Trip not found")
        return _row_to_trip(rows[0])

    def delete(self, owner_key: str, trip_id: str) -> None:
        try:
            result = (
                self._client.table(TABLE_NAME)
                .delete()
                .eq("owner_key", owner_key)
                .eq("id", trip_id)
                .execute()
            )
        except Exception as exc:  # noqa: BLE001
            raise TripStoreUnavailable(_friendly_db_error(exc)) from exc
        rows = result.data or []
        if not rows:
            # Some PostgREST configs return empty data on delete; verify with get
            try:
                self.get(owner_key, trip_id)
            except TripNotFound:
                return
            raise TripNotFound("Trip not found")


_memory_store = MemoryTripStore()


def _first_row(result: Any) -> dict[str, Any] | None:
    data = getattr(result, "data", None)
    if isinstance(data, list) and data:
        return data[0]
    if isinstance(data, dict):
        return data
    return None


def _friendly_db_error(exc: Exception) -> str:
    text = str(exc)
    lowered = text.lower()
    if "could not find the table" in lowered or "pgrst205" in lowered:
        return (
            "Supabase table public.saved_trips was not found. "
            "Run supabase/migrations/001_saved_trips.sql in the SQL Editor."
        )
    if "invalid path" in lowered or "pgrst125" in lowered:
        return (
            "Supabase URL looks invalid. Use https://YOUR_REF.supabase.co "
            "without /rest/v1."
        )
    if "jwt" in lowered or "api key" in lowered or "401" in lowered:
        return "Supabase rejected the API key. Check SUPABASE_SERVICE_ROLE_KEY."
    if len(text) > 220:
        return text[:220] + "..."
    return text or "Supabase request failed"


def get_trip_store() -> TripStore:
    mode = os.getenv("WANDERPLAN_TRIP_STORE", "").strip().lower()
    if mode == "memory":
        return _memory_store

    config = get_supabase_config()
    if not config["persistence_ready"]:
        raise TripStoreUnavailable(
            "Trip saving requires SUPABASE_SERVICE_ROLE_KEY in backend/.env "
            "(server-only). Auth is not implemented yet; the service role lets "
            "FastAPI save trips while RLS stays enabled for browser keys. "
            "For local tests without Supabase, set WANDERPLAN_TRIP_STORE=memory."
        )

    client = get_supabase_client(require_service_role=True)
    if client is None:
        raise TripStoreUnavailable(
            "Could not create a Supabase service-role client for trip persistence."
        )
    return SupabaseTripStore(client)
