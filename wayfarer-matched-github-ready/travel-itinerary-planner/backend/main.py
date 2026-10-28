"""
FastAPI entry point for the Travel Itinerary Planner.
Runs without Supabase credentials for local demo/health checks.
"""

import os
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import health, itineraries, trips

# Load backend/.env if present. override=True so edits to .env win over
# stale process env (uvicorn --reload does not clear previously loaded values).
load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

APP_NAME = os.getenv("APP_NAME", "Travel Itinerary Planner")

DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def parse_cors_origins(raw: str | None) -> list[str]:
    if not raw or not raw.strip():
        return DEFAULT_ORIGINS
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(title=APP_NAME, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_cors_origins(os.getenv("CORS_ORIGINS")),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(itineraries.router)
app.include_router(trips.router)


@app.get("/")
def root():
    return {
        "message": "Travel Itinerary Planner API",
        "docs": "/docs",
        "health": "/health",
        "generate_itinerary": "POST /api/itineraries/generate",
        "trips": {
            "save": "POST /api/trips",
            "list": "GET /api/trips",
            "get": "GET /api/trips/{trip_id}",
            "update": "PATCH /api/trips/{trip_id}",
            "delete": "DELETE /api/trips/{trip_id}",
        },
    }
