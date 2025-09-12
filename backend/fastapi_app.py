"""
FastAPI microservice exposing user profile endpoints for BeautyScan.

This service allows the Django app to fetch user profiles over HTTP
instead of calling the Django ORM directly.
"""

import os
import logging
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse


# Ensure Django is set up so we can reuse existing services/models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

try:
    import django
    django.setup()
except Exception:  # pragma: no cover - defensive
    # If setup fails, endpoints will still return error JSON
    pass

from backend.services.user_service import UserService  # noqa: E402


logger = logging.getLogger(__name__)
app = FastAPI(title="BeautyScan Profile Service", version="1.0.0")


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/user/profile")
def get_user_profile(user_id: int = Query(..., ge=1)) -> JSONResponse:
    try:
        service = UserService()
        profile = service._get_user_profile_via_orm(user_id)  # Reuse existing logic
        if not profile:
            return JSONResponse({
                "status": "error",
                "message": "Profil introuvable"
            }, status_code=404)
        return JSONResponse({
            "status": "success",
            "data": profile
        })
    except Exception as e:  # pragma: no cover - runtime safety
        logger.error(f"FastAPI error retrieving profile: {e}")
        return JSONResponse({
            "status": "error",
            "message": f"Erreur: {str(e)}"
        }, status_code=500)


