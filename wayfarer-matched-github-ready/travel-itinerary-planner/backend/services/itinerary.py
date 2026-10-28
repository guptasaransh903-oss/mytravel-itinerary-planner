
"""
WanderPlan itinerary generation service.

Uses Google Gemini AI when GEMINI_API_KEY is configured.
Retries temporary Gemini failures and falls back to a clearly labelled
rule-based demo itinerary when Gemini remains temporarily unavailable.
"""

from __future__ import annotations

import json
import os
import time
from datetime import date, timedelta

from dotenv import load_dotenv
from google import genai
from pydantic import ValidationError

from models.schemas import (
    ActivityBlock,
    DayPlan,
    ItineraryRequest,
    ItineraryResponse,
    TravelStyle,
)

# Load backend/.env even if this module is imported before dotenv is initialized.
load_dotenv(
    os.path.join(os.path.dirname(__file__), "..", ".env"),
    override=False,
)


ACTIVITY_POOL: dict[str, dict[str, list[str]]] = {
    "food": {
        "morning": [
            "Breakfast at a popular local cafe",
            "Visit a morning food market and sample street snacks",
        ],
        "afternoon": [
            "Lunch focused on regional specialties",
            "Cooking class or spice market tasting walk",
        ],
        "evening": [
            "Dinner at a local restaurant",
            "Explore a lively local street-food area",
        ],
    },
    "nature": {
        "morning": [
            "Sunrise walk or easy nature trail",
            "Visit a park, garden, or waterfront viewpoint",
        ],
        "afternoon": [
            "Outdoor excursion such as a lake, beach, or hill viewpoint",
            "Scenic picnic stop away from the busy center",
        ],
        "evening": [
            "Golden-hour nature lookout or botanical stroll",
            "Quiet outdoor cafe near greenery or water",
        ],
    },
    "culture": {
        "morning": [
            "Visit a museum or cultural center",
            "Guided neighborhood heritage walk",
        ],
        "afternoon": [
            "Explore an arts district or craft workshop",
            "Visit a local gallery or cultural venue",
        ],
        "evening": [
            "Explore a cultural performance or music venue",
            "Dinner in a historic or artsy quarter",
        ],
    },
    "shopping": {
        "morning": [
            "Browse a local bazaar or artisan market",
            "Explore independent boutiques and souvenir streets",
        ],
        "afternoon": [
            "Shop for local crafts, textiles, or design goods",
            "Visit a mall or covered market",
        ],
        "evening": [
            "Evening market stroll and people-watching",
            "Pick up gifts near the old town",
        ],
    },
    "history": {
        "morning": [
            "Tour a fort, palace, or historic landmark",
            "Visit a heritage museum or archaeological site",
        ],
        "afternoon": [
            "Walk a historic circuit with key monuments",
            "Join a local history walking tour",
        ],
        "evening": [
            "Sunset stop at a historic viewpoint",
            "Dinner near a heritage precinct",
        ],
    },
}


STYLE_PACE: dict[TravelStyle, dict[str, str]] = {
    TravelStyle.relaxed: {
        "prefix": "Easy-paced",
        "note": "Keep transfers short and leave buffer time.",
    },
    TravelStyle.balanced: {
        "prefix": "Balanced",
        "note": "Mix highlights with downtime.",
    },
    TravelStyle.adventurous: {
        "prefix": "Active",
        "note": "Prioritize experiences and longer outings.",
    },
}


STYLE_COST_FACTOR = {
    TravelStyle.relaxed: 0.9,
    TravelStyle.balanced: 1.0,
    TravelStyle.adventurous: 1.12,
}


def _ai_provider_configured() -> bool:
    """Check whether a Gemini API key is configured."""
    key = os.getenv("GEMINI_API_KEY", "").strip()

    if not key:
        return False

    lowered = key.lower()
    return not (
        lowered.startswith("your-")
        or lowered.endswith("-here")
        or "example" in lowered
    )


def _is_temporary_gemini_error(exc: Exception) -> bool:
    """Identify likely temporary Gemini overload, rate-limit, or server errors."""
    message = str(exc).upper()

    return any(
        marker in message
        for marker in (
            "503",
            "UNAVAILABLE",
            "HIGH DEMAND",
            "429",
            "RESOURCE_EXHAUSTED",
            "500",
            "502",
            "504",
            "TIMEOUT",
            "TIMED OUT",
            "OVERLOADED",
        )
    )


def _pick(pool: list[str], day_index: int, slot_offset: int) -> str:
    """Select a deterministic activity from a pool."""
    return pool[(day_index + slot_offset) % len(pool)]


def _build_day_activities(
    interests: list[str],
    day_index: int,
    style: TravelStyle,
) -> ActivityBlock:
    """Build activities for the demo generator."""
    ordered = (
        interests[day_index % len(interests):]
        + interests[:day_index % len(interests)]
    )
    primary = ordered[0]
    secondary = ordered[1 % len(ordered)]

    morning = [
        _pick(ACTIVITY_POOL[primary]["morning"], day_index, 0),
        STYLE_PACE[style]["note"],
    ]

    afternoon = [
        _pick(ACTIVITY_POOL[secondary]["afternoon"], day_index, 1),
        _pick(ACTIVITY_POOL[primary]["afternoon"], day_index, 2),
    ]

    evening = [
        _pick(ACTIVITY_POOL[primary]["evening"], day_index, 3),
    ]

    if style == TravelStyle.adventurous:
        afternoon.append(
            "Optional adventure activity, depending on local availability"
        )
    elif style == TravelStyle.relaxed:
        evening = [
            "Unhurried evening: cafe, short stroll, or early night"
        ]

    return ActivityBlock(
        morning=morning,
        afternoon=afternoon,
        evening=evening,
    )


def _allocate_daily_costs(
    budget_inr: int,
    trip_days: int,
    style: TravelStyle,
) -> list[int]:
    """Split the demo budget across trip days."""
    if style == TravelStyle.relaxed:
        usable = int(budget_inr * 0.88)
    elif style == TravelStyle.balanced:
        usable = int(budget_inr * 0.95)
    else:
        usable = budget_inr

    # Keep every day's estimate positive without exceeding the budget.
    usable = max(trip_days, usable)
    base = usable // trip_days
    remainder = usable % trip_days

    costs = [
        base + (1 if i < remainder else 0)
        for i in range(trip_days)
    ]

    if trip_days >= 3:
        mid = trip_days // 2
        bump = max(1, int(base * 0.08))
        transfer = min(bump, max(0, costs[0] - 1))
        costs[mid] += transfer
        costs[0] -= transfer

    return costs


def generate_rule_based_itinerary(
    request: ItineraryRequest,
) -> ItineraryResponse:
    """Build a deterministic demo itinerary from trip preferences."""
    trip_days = (request.end_date - request.start_date).days + 1

    daily_costs = _allocate_daily_costs(
        request.budget_inr,
        trip_days,
        request.travel_style,
    )

    style_meta = STYLE_PACE[request.travel_style]
    days: list[DayPlan] = []

    for i in range(trip_days):
        day_date = request.start_date + timedelta(days=i)
        interest_focus = request.interests[i % len(request.interests)]

        title = (
            f"{style_meta['prefix']} day in {request.destination} "
            f"- focus: {interest_focus}"
        )

        days.append(
            DayPlan(
                day=i + 1,
                date=day_date,
                title=title,
                estimated_cost_inr=daily_costs[i],
                activities=_build_day_activities(
                    request.interests,
                    i,
                    request.travel_style,
                ),
            )
        )

    return ItineraryResponse(
        destination=request.destination,
        start_date=request.start_date,
        end_date=request.end_date,
        travel_style=request.travel_style,
        interests=list(request.interests),
        currency="INR",
        budget_inr=request.budget_inr,
        total_estimated_cost_inr=sum(daily_costs),
        trip_days=trip_days,
        generator="rule_based_demo",
        generator_label="Rule-based demo generator (not AI)",
        days=days,
    )


def _generate_gemini_itinerary(
    request: ItineraryRequest,
) -> ItineraryResponse:
    """Generate and validate an itinerary using Google Gemini."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing.")

    client = genai.Client(api_key=api_key)
    trip_days = (request.end_date - request.start_date).days + 1

    prompt = f"""
You are WanderPlan, a helpful travel itinerary planner.

Create a personalized itinerary using:
Destination: {request.destination}
Start date: {request.start_date.isoformat()}
End date: {request.end_date.isoformat()}
Number of days: {trip_days}
Total budget: INR {request.budget_inr}
Travel style: {request.travel_style.value}
Interests: {", ".join(request.interests)}

Return only valid JSON with this structure:
{{
  "days": [
    {{
      "day": 1,
      "date": "{request.start_date.isoformat()}",
      "title": "A useful title for the day",
      "estimated_cost_inr": 1000,
      "activities": {{
        "morning": ["Activity 1", "Activity 2"],
        "afternoon": ["Activity 3"],
        "evening": ["Activity 4"]
      }}
    }}
  ]
}}

Rules:
- Return exactly {trip_days} days.
- Dates must be consecutive and match the requested dates.
- Include morning, afternoon and evening activities every day.
- Make activities relevant to the destination and selected interests.
- Match the selected travel style.
- Use integer, non-negative daily cost estimates in INR.
- The sum of all daily costs must not exceed INR {request.budget_inr}.
- Do not claim a booking has been made.
- Do not invent confirmed prices, opening hours, or reservations.
- Keep recommendations practical and avoid repeating the same activities.
"""

    # Retry likely temporary service errors up to three total attempts.
    response = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "temperature": 0.7,
                },
            )
            break

        except Exception as exc:
            if not _is_temporary_gemini_error(exc) or attempt == 2:
                raise

            wait_seconds = 2 * (attempt + 1)
            print(
                f"Temporary Gemini error on attempt {attempt + 1}/3. "
                f"Retrying in {wait_seconds} seconds."
            )
            time.sleep(wait_seconds)

    if response is None:
        raise RuntimeError("Gemini did not return a response after retries.")

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    result = json.loads(response.text)
    raw_days = result.get("days")

    if not isinstance(raw_days, list) or len(raw_days) != trip_days:
        raise ValueError(
            "Gemini returned an incorrect number of itinerary days."
        )

    days: list[DayPlan] = []

    for index, raw_day in enumerate(raw_days):
        day = DayPlan.model_validate(raw_day)
        expected_date = request.start_date + timedelta(days=index)

        if day.day != index + 1 or day.date != expected_date:
            raise ValueError(
                "Gemini returned incorrect day numbers or dates."
            )

        if day.estimated_cost_inr < 0:
            raise ValueError("Gemini returned a negative cost.")

        days.append(day)

    total = sum(day.estimated_cost_inr for day in days)

    # If the AI's estimates exceed the budget, scale them proportionally.
    # This adjusts estimates mathematically; it does not guarantee actual prices.
    if total > request.budget_inr:
        if total == 0:
            raise ValueError("Unable to adjust itinerary costs.")

        adjusted = [
            day.estimated_cost_inr * request.budget_inr // total
            for day in days
        ]

        remainder = request.budget_inr - sum(adjusted)

        for index in range(len(adjusted)):
            if remainder <= 0:
                break
            adjusted[index] += 1
            remainder -= 1

        for day, cost in zip(days, adjusted):
            day.estimated_cost_inr = cost

        total = sum(adjusted)

    return ItineraryResponse(
        destination=request.destination,
        start_date=request.start_date,
        end_date=request.end_date,
        travel_style=request.travel_style,
        interests=list(request.interests),
        currency="INR",
        budget_inr=request.budget_inr,
        total_estimated_cost_inr=total,
        trip_days=trip_days,
        generator="gemini_ai",
        generator_label="Generated by Google Gemini AI",
        days=days,
    )


def generate_itinerary(request: ItineraryRequest) -> ItineraryResponse:
    """
    Use Gemini when configured.

    Retry temporary errors in the Gemini call. If a temporary error persists,
    use the clearly labelled rule-based demo. Other errors are reported.
    """
    if not _ai_provider_configured():
        return generate_rule_based_itinerary(request)

    try:
        return _generate_gemini_itinerary(request)

    except Exception as exc:
        if _is_temporary_gemini_error(exc):
            print(
                "Gemini remains temporarily unavailable after retries. "
                "Using the labelled rule-based demo itinerary."
            )
            return generate_rule_based_itinerary(request)

        print(f"Gemini generation failed: {type(exc).__name__}: {exc}")

        raise ValueError(
            "Gemini could not generate the itinerary. "
            "Please check the API configuration and try again."
        ) from exc


def build_sample_itinerary(destination: str, days: int) -> dict:
    """Backwards-compatible helper used by early scaffolding."""
    safe_days = max(days, 1)
    start = date.today()
    end = start + timedelta(days=safe_days - 1)

    request = ItineraryRequest(
        destination=destination,
        start_date=start,
        end_date=end,
        budget_inr=max(5000, safe_days * 3000),
        travel_style=TravelStyle.balanced,
        interests=["culture", "food"],
    )

    return generate_rule_based_itinerary(request).model_dump(mode="json")
