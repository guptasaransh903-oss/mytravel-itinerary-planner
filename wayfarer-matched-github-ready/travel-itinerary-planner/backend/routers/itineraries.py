from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from models.schemas import ItineraryRequest, ItineraryResponse
from services.itinerary import generate_itinerary

router = APIRouter(prefix="/api/itineraries", tags=["itineraries"])


@router.post("/generate", response_model=ItineraryResponse)
def create_itinerary(payload: ItineraryRequest) -> ItineraryResponse:
    """
    Generate a day-by-day itinerary from trip preferences.

    Currently uses a rule-based demo generator (clearly labelled in the response).
    """
    try:
        return generate_itinerary(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 — return a useful client-facing error
        raise HTTPException(
            status_code=500,
            detail="Failed to generate itinerary. Please try again.",
        ) from exc
