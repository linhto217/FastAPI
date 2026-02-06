"""Fraud detection routes (Routes 13-15).

This module defines the API endpoints for fraud analysis and detection.
"""
from fastapi import APIRouter, Request

from banking_api.models.fraud import (
    FraudByType,
    FraudPredictionRequest,
    FraudPredictionResponse,
    FraudSummary,
)
from banking_api.services import fraud_detection_service

router = APIRouter(prefix="/api/fraud", tags=["Fraud"])


@router.get("/summary", response_model=FraudSummary)
def get_fraud_summary(request: Request) -> FraudSummary:
    """Get fraud overview statistics.

    Route 13: GET /api/fraud/summary

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    FraudSummary
        Fraud statistics including total frauds, flagged count,
        precision, and recall of the flagging system.
    """
    return fraud_detection_service.get_fraud_summary(request)


@router.get("/by-type", response_model=list[FraudByType])
def get_fraud_by_type(request: Request) -> list[FraudByType]:
    """Get fraud rate distribution by transaction type.

    Route 14: GET /api/fraud/by-type

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    list[FraudByType]
        Fraud statistics for each transaction type including
        total count, fraud count, and fraud rate.
    """
    return fraud_detection_service.get_fraud_by_type(request)


@router.post("/predict", response_model=FraudPredictionResponse)
def predict_fraud(
    request: Request,
    data: FraudPredictionRequest
) -> FraudPredictionResponse:
    """Predict fraud for a transaction using rule-based scoring.

    Route 15: POST /api/fraud/predict

    The scoring system uses the following deterministic rules:
    - Balance inconsistency: +0.3 if (oldbalanceOrg - amount) != newbalanceOrig
    - Risky type: +0.3 if type is CASH_OUT or TRANSFER
    - High amount: +0.4 if amount > 100,000
    - Rapid transactions: +0.3 if same customer has transactions within 1 hour

    A transaction is flagged as fraud if total score > 0.5.

    Parameters
    ----------
    request : Request
        The FastAPI request object.
    data : FraudPredictionRequest
        Transaction data for fraud prediction.

    Returns
    -------
    FraudPredictionResponse
        Prediction result with fraud flag and probability score.
    """
    return fraud_detection_service.predict_fraud(
        request,
        type_=data.type,
        amount=data.amount,
        old_balance_org=data.oldbalanceOrg,
        new_balance_orig=data.newbalanceOrig,
        name_orig=data.nameOrig,
        step=data.step
    )
