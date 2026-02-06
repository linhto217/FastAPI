"""Fraud detection Pydantic models.

This module defines the schemas for fraud-related requests and responses.
"""
from pydantic import BaseModel, Field


class FraudPredictionRequest(BaseModel):
    """Request model for fraud prediction.

    Attributes
    ----------
    type : str
        Transaction type.
    amount : float
        Transaction amount.
    oldbalanceOrg : float
        Initial balance of origin account.
    newbalanceOrig : float
        New balance of origin account after transaction.
    nameOrig : str, optional
        Origin customer ID for rapid transaction check.
    step : int, optional
        Time step for rapid transaction detection.
    """

    type: str = Field(..., description="Transaction type")
    amount: float = Field(..., ge=0, description="Transaction amount")
    oldbalanceOrg: float = Field(..., ge=0, description="Origin initial balance")
    newbalanceOrig: float = Field(..., ge=0, description="Origin final balance")
    nameOrig: str | None = Field(None, description="Origin customer ID")
    step: int | None = Field(None, ge=0, description="Time step")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "type": "TRANSFER",
                "amount": 3500.0,
                "oldbalanceOrg": 15000.0,
                "newbalanceOrig": 11500.0
            }
        }


class FraudPredictionResponse(BaseModel):
    """Response model for fraud prediction.

    Attributes
    ----------
    isFraud : bool
        Whether the transaction is predicted as fraudulent.
    probability : float
        Fraud probability score (0-1).
    """

    isFraud: bool = Field(..., description="Fraud prediction result")
    probability: float = Field(..., ge=0, le=1, description="Fraud probability")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "isFraud": True,
                "probability": 0.89
            }
        }


class FraudSummary(BaseModel):
    """Fraud overview statistics model.

    Attributes
    ----------
    total_frauds : int
        Total number of fraudulent transactions.
    flagged : int
        Number of system-flagged transactions.
    precision : float
        Flagging precision rate.
    recall : float
        Flagging recall rate.
    """

    total_frauds: int = Field(..., ge=0, description="Total fraud count")
    flagged: int = Field(..., ge=0, description="System flagged count")
    precision: float = Field(..., ge=0, le=1, description="Precision rate")
    recall: float = Field(..., ge=0, le=1, description="Recall rate")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "total_frauds": 8213,
                "flagged": 16,
                "precision": 0.95,
                "recall": 0.88
            }
        }


class FraudByType(BaseModel):
    """Fraud rate by transaction type model.

    Attributes
    ----------
    type : str
        Transaction type.
    total : int
        Total transactions of this type.
    fraud_count : int
        Fraudulent transactions of this type.
    fraud_rate : float
        Fraud rate for this type.
    """

    type: str = Field(..., description="Transaction type")
    total: int = Field(..., ge=0, description="Total transactions")
    fraud_count: int = Field(..., ge=0, description="Fraud count")
    fraud_rate: float = Field(..., ge=0, le=1, description="Fraud rate")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "type": "TRANSFER",
                "total": 400000,
                "fraud_count": 4097,
                "fraud_rate": 0.0102
            }
        }
