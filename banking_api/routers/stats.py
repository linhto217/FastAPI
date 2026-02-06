"""Statistics routes (Routes 9-12).

This module defines the API endpoints for statistical operations.
"""
from fastapi import APIRouter, Request

from banking_api.models.stats import (
    AmountDistribution,
    DailyStats,
    StatsOverview,
    TypeStats,
)
from banking_api.services import stats_service

router = APIRouter(prefix="/api/stats", tags=["Statistics"])


@router.get("/overview", response_model=StatsOverview)
def get_overview(request: Request) -> StatsOverview:
    """Get global dataset statistics.

    Route 9: GET /api/stats/overview

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    StatsOverview
        Global statistics including total transactions, fraud rate,
        average amount, and most common type.
    """
    return stats_service.get_overview(request)


@router.get("/amount-distribution", response_model=AmountDistribution)
def get_amount_distribution(request: Request) -> AmountDistribution:
    """Get histogram of transaction amounts.

    Route 10: GET /api/stats/amount-distribution

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    AmountDistribution
        Histogram bins and counts showing distribution of
        transaction amounts across value ranges.
    """
    return stats_service.get_amount_distribution(request)


@router.get("/by-type", response_model=list[TypeStats])
def get_stats_by_type(request: Request) -> list[TypeStats]:
    """Get statistics grouped by transaction type.

    Route 11: GET /api/stats/by-type

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    list[TypeStats]
        Total amount and average transaction count for each type.
    """
    return stats_service.get_stats_by_type(request)


@router.get("/daily", response_model=list[DailyStats])
def get_daily_stats(request: Request) -> list[DailyStats]:
    """Get daily average and transaction volume.

    Route 12: GET /api/stats/daily

    Statistics are grouped by day (24 steps = 1 day in the simulation).

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    list[DailyStats]
        Daily transaction count, average amount, and total volume.
    """
    return stats_service.get_daily_stats(request)
