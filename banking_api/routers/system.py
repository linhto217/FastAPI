"""System routes (Routes 19-20).

This module defines the API endpoints for system health and metadata.
"""
from fastapi import APIRouter, Request

from banking_api.models.responses import HealthResponse, MetadataResponse
from banking_api.services import system_service

router = APIRouter(prefix="/api/system", tags=["System"])


@router.get("/health", response_model=HealthResponse)
def health_check(request: Request) -> HealthResponse:
    """Check API health status.

    Route 19: GET /api/system/health

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    HealthResponse
        Health status including uptime and dataset load status.
    """
    return system_service.get_health(request)


@router.get("/metadata", response_model=MetadataResponse)
def get_metadata(request: Request) -> MetadataResponse:
    """Get service version and metadata.

    Route 20: GET /api/system/metadata

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    MetadataResponse
        Service version, last update timestamp, test mode status,
        and total transaction count.
    """
    return system_service.get_metadata(request)
