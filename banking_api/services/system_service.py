"""System service module.

This module provides business logic for system health checks
and metadata endpoints.
"""
import os
from datetime import datetime

from fastapi import Request

from banking_api import __version__
from banking_api.models.responses import HealthResponse, MetadataResponse


def get_health(request: Request) -> HealthResponse:
    """Check API health status.

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    HealthResponse
        Health check result with uptime and dataset status.
    """
    # Check if data is loaded
    dataset_loaded = hasattr(request.app.state, "dal") and request.app.state.dal is not None

    # Calculate uptime
    start_time: datetime = request.app.state.start_time
    uptime_delta = datetime.now() - start_time

    hours, remainder = divmod(int(uptime_delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        uptime_str = f"{hours}h {minutes}min"
    elif minutes > 0:
        uptime_str = f"{minutes}min {seconds}s"
    else:
        uptime_str = f"{seconds}s"

    status = "ok" if dataset_loaded else "error"

    return HealthResponse(
        status=status,
        uptime=uptime_str,
        dataset_loaded=dataset_loaded
    )


def get_metadata(request: Request) -> MetadataResponse:
    """Get service metadata.

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    MetadataResponse
        Service version, last update, and configuration details.
    """
    # Get test mode status
    test_mode = os.getenv("TEST_MODE", "0").lower() in ("1", "true", "yes")

    # Get total transactions
    total_transactions = 0
    if hasattr(request.app.state, "dal") and request.app.state.dal is not None:
        df = request.app.state.dal.get_dataframe()
        total_transactions = len(df)

    # Get load time as last update
    last_update = request.app.state.load_time

    return MetadataResponse(
        version=__version__,
        last_update=last_update,
        test_mode=test_mode,
        total_transactions=total_transactions
    )
