"""
health.py - Health check endpoint.
"""

from fastapi import APIRouter
from backend.app.services.data_loader import get_actuals, get_forecasts
from backend.app.models.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return system health status and dataset row counts."""
    act = get_actuals()
    fc = get_forecasts()
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        datasetsLoaded=True,
        actualsRowCount=len(act),
        forecastsRowCount=len(fc)
    )
