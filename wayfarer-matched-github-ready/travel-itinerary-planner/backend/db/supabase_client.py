"""
Supabase client helper.

Demo mode: starts without real credentials (placeholder .env values are ignored).
Configured mode: creates a supabase-py client when SUPABASE_URL and a key are set.

Trip persistence requires SUPABASE_SERVICE_ROLE_KEY on the backend so RLS can stay
enabled for anon/authenticated clients. The service-role key must never be sent
to the frontend.
"""

from __future__ import annotations

import os
from typing import Any
from pathlib import Path

from dotenv import load_dotenv

# Prefer values from backend/.env over any earlier process env (e.g. leftover
# placeholders after editing .env while uvicorn --reload kept the process alive).
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_FILE, override=True)

# Env var names expected by this module (keep in sync with backend/.env.example)
ENV_SUPABASE_URL = "SUPABASE_URL"
ENV_SUPABASE_ANON_KEY = "SUPABASE_ANON_KEY"
ENV_SUPABASE_SERVICE_ROLE_KEY = "SUPABASE_SERVICE_ROLE_KEY"

# Only treat known template strings as missing credentials (not broad substrings).
_PLACEHOLDER_VALUES = {
    "https://your-project-ref.supabase.co",
    "your-anon-key-here",
    "your-service-role-key-here",
}


def _looks_like_placeholder(value: str | None) -> bool:
    if not value:
        return True
    normalized = value.strip().lower()
    return normalized in _PLACEHOLDER_VALUES or normalized.startswith("your-")


def _read_env(name: str) -> str:
    return os.getenv(name, "").strip()


def normalize_supabase_url(url: str) -> str:
    """
    Accept either the project URL or a mistaken /rest/v1 URL from the dashboard.
    supabase-py expects https://<ref>.supabase.co with no /rest/v1 suffix.
    """
    cleaned = url.strip().rstrip("/")
    for suffix in ("/rest/v1", "/rest/v1/"):
        if cleaned.lower().endswith(suffix.rstrip("/")):
            cleaned = cleaned[: -len(suffix.rstrip("/"))]
            cleaned = cleaned.rstrip("/")
    return cleaned


def get_supabase_config() -> dict[str, Any]:
    url = normalize_supabase_url(_read_env(ENV_SUPABASE_URL))
    anon_key = _read_env(ENV_SUPABASE_ANON_KEY)
    service_key = _read_env(ENV_SUPABASE_SERVICE_ROLE_KEY)

    has_url = bool(url) and not _looks_like_placeholder(url)
    has_anon = bool(anon_key) and not _looks_like_placeholder(anon_key)
    has_service = bool(service_key) and not _looks_like_placeholder(service_key)
    has_key = has_anon or has_service

    return {
        "url_configured": has_url,
        "key_configured": has_key,
        "configured": has_url and has_key,
        "using_service_role": has_service,
        "persistence_ready": has_url and has_service,
    }


def get_supabase_status() -> dict[str, Any]:
    config = get_supabase_config()
    if config["configured"]:
        mode = "configured"
        if config["persistence_ready"]:
            message = "Supabase configured; trip persistence available via service role."
        else:
            message = (
                "Supabase env vars are set, but SUPABASE_SERVICE_ROLE_KEY is missing. "
                "Generation works; saving trips requires the service-role key on the backend."
            )
    else:
        mode = "demo"
        message = "Running without Supabase credentials (demo mode)."

    # Never include URL or key values in status responses
    return {
        "mode": mode,
        "message": message,
        "url_configured": config["url_configured"],
        "key_configured": config["key_configured"],
        "configured": config["configured"],
        "persistence_ready": config["persistence_ready"],
    }


def get_supabase_client(*, require_service_role: bool = False):
    """
    Return a supabase-py client, or None in demo mode.

    When require_service_role=True (trip CRUD), only the service-role key is used
    so RLS can remain enforced for anon/authenticated keys.
    """
    config = get_supabase_config()
    url = normalize_supabase_url(_read_env(ENV_SUPABASE_URL))

    if require_service_role:
        if not config["persistence_ready"]:
            return None
        key = _read_env(ENV_SUPABASE_SERVICE_ROLE_KEY)
    else:
        if not config["configured"]:
            return None
        service_key = _read_env(ENV_SUPABASE_SERVICE_ROLE_KEY)
        anon_key = _read_env(ENV_SUPABASE_ANON_KEY)
        key = (
            service_key
            if service_key and not _looks_like_placeholder(service_key)
            else anon_key
        )

    from supabase import create_client

    return create_client(url, key)
