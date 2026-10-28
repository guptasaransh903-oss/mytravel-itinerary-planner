from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class TravelStyle(str, Enum):
    relaxed = "relaxed"
    balanced = "balanced"
    adventurous = "adventurous"


Interest = Literal["food", "nature", "culture", "shopping", "history"]
ALLOWED_INTERESTS = {"food", "nature", "culture", "shopping", "history"}


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "travel-itinerary-planner-api"
    supabase: dict = Field(default_factory=dict)


class ItineraryRequest(BaseModel):
    """Trip preferences for itinerary generation."""

    destination: str = Field(..., min_length=2, max_length=120, examples=["Goa, India"])
    start_date: date = Field(..., examples=["2026-11-01"])
    end_date: date = Field(..., examples=["2026-11-05"])
    budget_inr: int = Field(..., gt=0, le=10_000_000, examples=[50000])
    travel_style: TravelStyle = Field(..., examples=["balanced"])
    interests: list[Interest] = Field(
        ...,
        min_length=1,
        examples=[["food", "nature", "culture"]],
    )

    @field_validator("destination")
    @classmethod
    def strip_destination(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("destination must be at least 2 characters")
        return cleaned

    @field_validator("interests")
    @classmethod
    def unique_interests(cls, value: list[Interest]) -> list[Interest]:
        unique = list(dict.fromkeys(value))
        invalid = [item for item in unique if item not in ALLOWED_INTERESTS]
        if invalid:
            raise ValueError(f"unsupported interests: {invalid}")
        return unique

    @model_validator(mode="after")
    def validate_date_range(self) -> "ItineraryRequest":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        trip_days = (self.end_date - self.start_date).days + 1
        if trip_days > 30:
            raise ValueError("trip length cannot exceed 30 days")
        return self


class ActivityBlock(BaseModel):
    morning: list[str]
    afternoon: list[str]
    evening: list[str]


class DayPlan(BaseModel):
    day: int
    date: date
    title: str
    estimated_cost_inr: int
    activities: ActivityBlock


class ItineraryResponse(BaseModel):
    destination: str
    start_date: date
    end_date: date
    travel_style: TravelStyle
    interests: list[str]
    currency: str = "INR"
    budget_inr: int
    total_estimated_cost_inr: int
    trip_days: int
    generator: str
    generator_label: str
    days: list[DayPlan]


class SaveTripRequest(BaseModel):
    """Persist trip preferences together with a generated itinerary."""

    preferences: ItineraryRequest
    itinerary: ItineraryResponse
    title: str | None = Field(default=None, max_length=160)

    @model_validator(mode="after")
    def preferences_match_itinerary(self) -> "SaveTripRequest":
        pref = self.preferences
        itin = self.itinerary
        if pref.destination.strip().lower() != itin.destination.strip().lower():
            raise ValueError("itinerary.destination must match preferences.destination")
        if pref.start_date != itin.start_date or pref.end_date != itin.end_date:
            raise ValueError("itinerary dates must match preferences dates")
        if pref.travel_style != itin.travel_style:
            raise ValueError("itinerary.travel_style must match preferences.travel_style")
        return self


class UpdateTripRequest(BaseModel):
    """Partial update for a saved trip."""

    title: str | None = Field(default=None, min_length=1, max_length=160)
    preferences: ItineraryRequest | None = None
    itinerary: ItineraryResponse | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "UpdateTripRequest":
        if self.title is None and self.preferences is None and self.itinerary is None:
            raise ValueError("Provide title, preferences, and/or itinerary to update")
        if self.preferences is not None and self.itinerary is not None:
            if (
                self.preferences.destination.strip().lower()
                != self.itinerary.destination.strip().lower()
            ):
                raise ValueError("itinerary.destination must match preferences.destination")
            if (
                self.preferences.start_date != self.itinerary.start_date
                or self.preferences.end_date != self.itinerary.end_date
            ):
                raise ValueError("itinerary dates must match preferences dates")
        return self


class SavedTripSummary(BaseModel):
    id: str
    title: str
    destination: str
    start_date: date
    end_date: date
    budget_inr: int
    travel_style: TravelStyle
    interests: list[str]
    total_estimated_cost_inr: int
    trip_days: int
    created_at: str
    updated_at: str


class SavedTrip(SavedTripSummary):
    preferences: ItineraryRequest
    itinerary: ItineraryResponse


class SavedTripListResponse(BaseModel):
    trips: list[SavedTripSummary]
    count: int


# Keep a light alias for older references
class TripPreferences(ItineraryRequest):
    """Backward-compatible alias for ItineraryRequest."""
