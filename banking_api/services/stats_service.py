"""Statistics service module.

This module provides business logic for statistical operations,
returning precomputed values from app.state.cached_stats.
"""
from typing import Any

from fastapi import Request

from banking_api.models.stats import (
    AmountDistribution,
    DailyStats,
    StatsOverview,
    TypeStats,
)


def get_overview(request: Request) -> StatsOverview:
    """Get global dataset statistics.

    Returns precomputed statistics from app.state.cached_stats.

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
    stats = request.app.state.cached_stats["overview"]
    return StatsOverview(**stats)


def get_amount_distribution(request: Request) -> AmountDistribution:
    """Get histogram of transaction amounts.

    Returns precomputed distribution from app.state.cached_stats.

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    AmountDistribution
        Histogram bins and counts.
    """
    stats = request.app.state.cached_stats["amount_distribution"]
    return AmountDistribution(**stats)


def get_stats_by_type(request: Request) -> list[TypeStats]:
    """Get statistics grouped by transaction type.

    Returns precomputed type statistics from app.state.cached_stats.

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    list[TypeStats]
        Statistics for each transaction type.
    """
    stats = request.app.state.cached_stats["by_type"]
    return [TypeStats(**s) for s in stats]


def get_daily_stats(request: Request) -> list[DailyStats]:
    """Get daily transaction statistics.

    Returns precomputed daily stats from app.state.cached_stats.

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    list[DailyStats]
        Daily statistics including transaction count and amounts.
    """
    stats = request.app.state.cached_stats["daily"]
    return [DailyStats(**s) for s in stats]


def compute_all_stats(df: Any) -> dict[str, Any]:
    """Compute all statistics from the DataFrame.

    This function is called at startup to precompute all
    statistics and store them in app.state.cached_stats.

    Parameters
    ----------
    df : pd.DataFrame
        The transaction DataFrame.

    Returns
    -------
    dict[str, Any]
        Dictionary containing all precomputed statistics.
    """
    import pandas as pd

    # Overview statistics
    type_counts = df["type"].value_counts()
    most_common_type = type_counts.index[0] if len(type_counts) > 0 else "N/A"

    overview = {
        "total_transactions": len(df),
        "fraud_rate": float(df["isFraud"].mean()),
        "avg_amount": float(df["amount"].mean()),
        "most_common_type": str(most_common_type)
    }

    # Amount distribution
    bins = [0, 100, 500, 1000, 5000, 10000, 50000, 100000, float("inf")]
    bin_labels = [
        "0-100", "100-500", "500-1k", "1k-5k",
        "5k-10k", "10k-50k", "50k-100k", "100k+"
    ]

    amount_bins = pd.cut(df["amount"], bins=bins, labels=bin_labels)
    bin_counts = amount_bins.value_counts().sort_index()

    amount_distribution = {
        "bins": bin_labels,
        "counts": [int(bin_counts.get(label, 0)) for label in bin_labels]
    }

    # Stats by type
    type_stats = df.groupby("type", observed=True).agg(
        count=("amount", "count"),
        avg_amount=("amount", "mean"),
        total_amount=("amount", "sum")
    ).reset_index()

    by_type = [
        {
            "type": str(row["type"]),
            "count": int(row["count"]),
            "avg_amount": float(row["avg_amount"]),
            "total_amount": float(row["total_amount"])
        }
        for _, row in type_stats.iterrows()
    ]

    # Daily stats (24 steps = 1 day)
    df_copy = df.copy()
    df_copy["day"] = df_copy["step"] // 24

    daily_agg = df_copy.groupby("day").agg(
        transaction_count=("amount", "count"),
        avg_amount=("amount", "mean"),
        total_amount=("amount", "sum")
    ).reset_index()

    daily = [
        {
            "step_range": f"{int(row['day'] * 24 + 1)}-{int((row['day'] + 1) * 24)}",
            "transaction_count": int(row["transaction_count"]),
            "avg_amount": float(row["avg_amount"]),
            "total_amount": float(row["total_amount"])
        }
        for _, row in daily_agg.iterrows()
    ]

    return {
        "overview": overview,
        "amount_distribution": amount_distribution,
        "by_type": by_type,
        "daily": daily
    }
