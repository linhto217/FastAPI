"""Fraud detection service module.

This module provides business logic for fraud analysis and prediction
using deterministic rule-based heuristics.
"""
from typing import Any, Optional

from fastapi import Request

from banking_api.models.fraud import (
    FraudByType,
    FraudPredictionResponse,
    FraudSummary,
)


# Fraud detection constants
RISKY_TYPES = {"CASH_OUT", "TRANSFER"}
HIGH_AMOUNT_THRESHOLD = 100000.0
BALANCE_TOLERANCE = 0.01
RAPID_TRANSACTION_STEP_GAP = 1  # 1 hour


def predict_fraud(
    request: Request,
    type_: str,
    amount: float,
    old_balance_org: float,
    new_balance_orig: float,
    name_orig: Optional[str] = None,
    step: Optional[int] = None
) -> FraudPredictionResponse:
    """Predict fraud using deterministic rule-based heuristics.

    The scoring system uses the following rules:
    - Balance inconsistency: +0.3 if expected balance doesn't match
    - Risky type: +0.3 if transaction is CASH_OUT or TRANSFER
    - High amount: +0.4 if amount > 100,000
    - Rapid transactions: +0.3 if customer has transactions within 1 hour

    A transaction is flagged as fraud if the total score exceeds 0.5.

    Parameters
    ----------
    request : Request
        The FastAPI request object.
    type_ : str
        Transaction type.
    amount : float
        Transaction amount.
    old_balance_org : float
        Origin account balance before transaction.
    new_balance_orig : float
        Origin account balance after transaction.
    name_orig : str, optional
        Origin customer ID for rapid transaction check.
    step : int, optional
        Time step for rapid transaction detection.

    Returns
    -------
    FraudPredictionResponse
        Prediction result with fraud flag and probability.
    """
    score = 0.0

    # Rule 1: Balance inconsistency
    # Expected new balance = old balance - amount (for outgoing transactions)
    expected_balance = old_balance_org - amount
    balance_diff = abs(expected_balance - new_balance_orig)

    if balance_diff > BALANCE_TOLERANCE:
        score += 0.3

    # Rule 2: Risky transaction type
    if type_ in RISKY_TYPES:
        score += 0.3

    # Rule 3: High amount
    if amount > HIGH_AMOUNT_THRESHOLD:
        score += 0.4

    # Rule 4: Rapid transactions (if customer info provided)
    if name_orig and step is not None:
        dal = request.app.state.dal
        timeline = dal.get_customer_timeline(name_orig)

        for tx_step, _ in timeline:
            if tx_step != step and abs(tx_step - step) <= RAPID_TRANSACTION_STEP_GAP:
                score += 0.3
                break

    # Cap probability at 1.0
    probability = min(score, 1.0)
    is_fraud = probability > 0.5

    return FraudPredictionResponse(
        isFraud=is_fraud,
        probability=round(probability, 2)
    )


def get_fraud_summary(request: Request) -> FraudSummary:
    """Get fraud overview statistics.

    Returns precomputed fraud summary from app.state.cached_stats.

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    FraudSummary
        Fraud statistics including totals, precision, and recall.
    """
    stats = request.app.state.cached_stats["fraud_summary"]
    return FraudSummary(**stats)


def get_fraud_by_type(request: Request) -> list[FraudByType]:
    """Get fraud rate distribution by transaction type.

    Returns precomputed fraud-by-type statistics from app.state.cached_stats.

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    list[FraudByType]
        Fraud statistics for each transaction type.
    """
    stats = request.app.state.cached_stats["fraud_by_type"]
    return [FraudByType(**s) for s in stats]


def compute_fraud_stats(df: Any) -> dict[str, Any]:
    """Compute fraud statistics from the DataFrame.

    This function is called at startup to precompute fraud
    statistics and store them in app.state.cached_stats.

    Parameters
    ----------
    df : pd.DataFrame
        The transaction DataFrame.

    Returns
    -------
    dict[str, Any]
        Dictionary containing fraud_summary and fraud_by_type stats.
    """
    total_frauds = int(df["isFraud"].sum())
    flagged = int(df["isFlaggedFraud"].sum())

    # Calculate precision and recall
    # Precision = flagged_and_fraud / flagged
    # Recall = flagged_and_fraud / total_frauds
    flagged_and_fraud = int(((df["isFraud"] == 1) & (df["isFlaggedFraud"] == 1)).sum())

    precision = flagged_and_fraud / flagged if flagged > 0 else 0.0
    recall = flagged_and_fraud / total_frauds if total_frauds > 0 else 0.0

    fraud_summary = {
        "total_frauds": total_frauds,
        "flagged": flagged,
        "precision": round(precision, 2),
        "recall": round(recall, 2)
    }

    # Fraud by type
    type_fraud = df.groupby("type", observed=True).agg(
        total=("isFraud", "count"),
        fraud_count=("isFraud", "sum")
    ).reset_index()

    fraud_by_type = [
        {
            "type": str(row["type"]),
            "total": int(row["total"]),
            "fraud_count": int(row["fraud_count"]),
            "fraud_rate": round(
                float(row["fraud_count"]) / float(row["total"])
                if row["total"] > 0 else 0.0,
                4
            )
        }
        for _, row in type_fraud.iterrows()
    ]

    return {
        "fraud_summary": fraud_summary,
        "fraud_by_type": fraud_by_type
    }
