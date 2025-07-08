"""Location Suggest 라우터"""
# pyright: reportImportCycles=false
from __future__ import annotations

from typing import TYPE_CHECKING, cast

from fastapi import APIRouter, FastAPI, HTTPException, Request

from src.inference.api.schemas import LocationSuggestRequest, LocationSuggestResponse

if TYPE_CHECKING:
    from src.inference.api.handlers.location_handler import LocationHandler

router = APIRouter()

@router.post("/api/location-suggest", response_model=LocationSuggestResponse)
async def suggest_locations(request_body: LocationSuggestRequest, request: Request) -> LocationSuggestResponse:
    app = cast(FastAPI, request.app)
    location_handler = cast("LocationHandler | None", getattr(app.state, "location_handler", None))
    if location_handler is None:
        raise HTTPException(status_code=503, detail="Location handler not ready")
    if not location_handler.enabled:
        raise HTTPException(status_code=503, detail="Location handler disabled. Please configure NEUTRINO_USER_ID and NEUTRINO_API_KEY environment variables.")
    try:
        suggestions = location_handler.suggest_locations(request_body.query)
        return LocationSuggestResponse(suggestions=suggestions)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Location suggestion service error: {exc}") 