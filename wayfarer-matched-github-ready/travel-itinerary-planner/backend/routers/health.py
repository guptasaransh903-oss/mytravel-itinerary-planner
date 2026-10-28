from fastapi import APIRouter

from db.supabase_client import get_supabase_status

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Lightweight health endpoint for local development and frontend checks."""
    supabase = get_supabase_status()
    return {
        "status": "ok",
        "service": "travel-itinerary-planner-api",
        "supabase": supabase,
    }
