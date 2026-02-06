"""Transaction Pydantic models.

This module defines the schemas for transaction data,
including request and response models.
"""
from typing import Optional

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    """Transaction data model.

    Attributes
    ----------
    id : str
        Unique transaction identifier (tx_XXXXXXX format).
    step : int
        Time step (1 unit = 1 hour of simulation).
    type : str
        Transaction type (CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER).
    amount : float
        Transaction amount.
    nameOrig : str
        Customer ID initiating the transaction.
    oldbalanceOrg : float
        Initial balance of origin account.
    newbalanceOrig : float
        New balance of origin account after transaction.
    nameDest : str
        Customer ID receiving the transaction.
    oldbalanceDest : float
        Initial balance of destination account.
    newbalanceDest : float
        New balance of destination account after transaction.
    isFraud : int
        Fraud indicator (0 = legitimate, 1 = fraud).
    isFlaggedFraud : int
        System flagged fraud indicator.
    """

    id: str = Field(..., description="Unique transaction identifier")
    step: int = Field(..., ge=0, description="Time step")
    type: str = Field(..., description="Transaction type")
    amount: float = Field(..., ge=0, description="Transaction amount")
    nameOrig: str = Field(..., description="Origin customer ID")
    oldbalanceOrg: float = Field(..., ge=0, description="Origin initial balance")
    newbalanceOrig: float = Field(..., ge=0, description="Origin final balance")
    nameDest: str = Field(..., description="Destination customer ID")
    oldbalanceDest: float = Field(..., ge=0, description="Destination initial balance")
    newbalanceDest: float = Field(..., ge=0, description="Destination final balance")
    isFraud: int = Field(..., ge=0, le=1, description="Fraud indicator")
    isFlaggedFraud: int = Field(..., ge=0, le=1, description="Flagged fraud indicator")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "id": "tx_0000001",
                "step": 1,
                "type": "TRANSFER",
                "amount": 9839.64,
                "nameOrig": "C1231006815",
                "oldbalanceOrg": 170136.0,
                "newbalanceOrig": 160296.36,
                "nameDest": "M1979787155",
                "oldbalanceDest": 0.0,
                "newbalanceDest": 0.0,
                "isFraud": 0,
                "isFlaggedFraud": 0
            }
        }


class TransactionSummary(BaseModel):
    """Simplified transaction model for list responses.

    Attributes
    ----------
    id : str
        Unique transaction identifier.
    amount : float
        Transaction amount.
    type : str
        Transaction type.
    """

    id: str
    amount: float
    type: str


class SearchRequest(BaseModel):
    """Multi-criteria search request model.

    Attributes
    ----------
    type : str, optional
        Filter by transaction type.
    isFraud : int, optional
        Filter by fraud status (0 or 1).
    amount_range : list[float], optional
        Filter by amount range [min, max].
    """

    type: Optional[str] = Field(None, description="Transaction type filter")
    isFraud: Optional[int] = Field(None, ge=0, le=1, description="Fraud filter")
    amount_range: Optional[list[float]] = Field(
        None,
        min_length=2,
        max_length=2,
        description="Amount range [min, max]"
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "type": "TRANSFER",
                "isFraud": 1,
                "amount_range": [1000, 5000]
            }
        }
