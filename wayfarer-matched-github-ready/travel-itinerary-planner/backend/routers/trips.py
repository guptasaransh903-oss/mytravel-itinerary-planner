from fastapi import APIRouter, Header, HTTPException, Response, status
from pydantic import ValidationError

from models.schemas import (
    SavedTrip,
    SavedTripListResponse,
    SaveTripRequest,
    UpdateTripRequest,
)
from services.trips import (
    OWNER_KEY_HEADER,
    TripNotFound,
    TripStoreUnavailable,
    get_trip_store,
    validate_owner_key,
)

router = APIRouter(prefix="/api/trips", tags=["trips"])


def _owner_from_header(x_wanderplan_owner_key: str | None) -> str:
    try:
        return validate_owner_key(x_wanderplan_owner_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("", response_model=SavedTrip, status_code=status.HTTP_201_CREATED)
def save_trip(
    payload: SaveTripRequest,
    x_wanderplan_owner_key: str | None = Header(default=None, alias=OWNER_KEY_HEADER),
) -> SavedTrip:
    """Save trip preferences and a generated itinerary for the current owner key."""
    owner_key = _owner_from_header(x_wanderplan_owner_key)
    try:
        return get_trip_store().create(owner_key, payload)
    except TripStoreUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail="Failed to save trip. Please try again."
        ) from exc


@router.get("", response_model=SavedTripListResponse)
def list_trips(
    x_wanderplan_owner_key: str | None = Header(default=None, alias=OWNER_KEY_HEADER),
) -> SavedTripListResponse:
    owner_key = _owner_from_header(x_wanderplan_owner_key)
    try:
        trips = get_trip_store().list(owner_key)
        return SavedTripListResponse(trips=trips, count=len(trips))
    except TripStoreUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail="Failed to list saved trips."
        ) from exc


@router.get("/{trip_id}", response_model=SavedTrip)
def get_trip(
    trip_id: str,
    x_wanderplan_owner_key: str | None = Header(default=None, alias=OWNER_KEY_HEADER),
) -> SavedTrip:
    owner_key = _owner_from_header(x_wanderplan_owner_key)
    try:
        return get_trip_store().get(owner_key, trip_id)
    except TripNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TripStoreUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail="Failed to load saved trip."
        ) from exc


@router.patch("/{trip_id}", response_model=SavedTrip)
def update_trip(
    trip_id: str,
    payload: UpdateTripRequest,
    x_wanderplan_owner_key: str | None = Header(default=None, alias=OWNER_KEY_HEADER),
) -> SavedTrip:
    owner_key = _owner_from_header(x_wanderplan_owner_key)
    try:
        return get_trip_store().update(owner_key, trip_id, payload)
    except TripNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TripStoreUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail="Failed to update trip."
        ) from exc


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: str,
    x_wanderplan_owner_key: str | None = Header(default=None, alias=OWNER_KEY_HEADER),
) -> Response:
    owner_key = _owner_from_header(x_wanderplan_owner_key)
    try:
        get_trip_store().delete(owner_key, trip_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except TripNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TripStoreUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail="Failed to delete trip."
        ) from exc
