"""API response wrapper models.

This module defines generic response wrappers for consistent API responses.
"""
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper.

    Attributes
    ----------
    page : int
        Current page number.
    limit : int
        Items per page.
    total : int
        Total number of items.
    data : list[T]
        List of items for current page.
    """

    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Items per page")
    total: int = Field(..., ge=0, description="Total items")
    data: list = Field(..., description="Page data")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "page": 1,
                "limit": 10,
                "total": 1000,
                "data": []
            }
        }


class TransactionListResponse(BaseModel):
    """Transaction list response matching spec format.

    Attributes
    ----------
    page : int
        Current page number.
    transactions : list
        List of transactions.
    """

    page: int = Field(..., ge=1, description="Current page number")
    transactions: list = Field(..., description="Transaction list")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "page": 1,
                "transactions": [
                    {"id": "tx_0001", "amount": 500.0, "type": "CASH_OUT"}
                ]
            }
        }


class HealthResponse(BaseModel):
    """Health check response model.

    Attributes
    ----------
    status : str
        Service status (ok/error).
    uptime : str
        Service uptime duration.
    dataset_loaded : bool
        Whether the dataset is loaded successfully.
    """

    status: str = Field(..., description="Service status")
    uptime: str = Field(..., description="Service uptime")
    dataset_loaded: bool = Field(..., description="Dataset load status")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "status": "ok",
                "uptime": "2h 15min",
                "dataset_loaded": True
            }
        }


class MetadataResponse(BaseModel):
    """Service metadata response model.

    Attributes
    ----------
    version : str
        API version.
    last_update : datetime
        Last update timestamp.
    test_mode : bool
        Whether running in test mode.
    total_transactions : int
        Number of loaded transactions.
    """

    version: str = Field(..., description="API version")
    last_update: datetime = Field(..., description="Last update timestamp")
    test_mode: bool = Field(..., description="Test mode status")
    total_transactions: int = Field(..., ge=0, description="Transaction count")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "version": "1.0.0",
                "last_update": "2025-12-20T22:00:00Z",
                "test_mode": False,
                "total_transactions": 6362620
            }
        }


class DeleteResponse(BaseModel):
    """Delete operation response model.

    Attributes
    ----------
    success : bool
        Whether deletion was successful.
    message : str
        Operation message.
    """

    success: bool = Field(..., description="Operation success")
    message: str = Field(..., description="Operation message")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Transaction tx_0000001 deleted successfully"
            }
        }
