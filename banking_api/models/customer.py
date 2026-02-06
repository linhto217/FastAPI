"""Customer Pydantic models.

This module defines the schemas for customer data.
"""
from pydantic import BaseModel, Field


class Customer(BaseModel):
    """Customer profile model.

    Attributes
    ----------
    id : str
        Unique customer identifier.
    transactions_count : int
        Total number of transactions by this customer.
    avg_amount : float
        Average transaction amount.
    fraudulent : bool
        Whether the customer has any fraudulent transactions.
    """

    id: str = Field(..., description="Customer identifier")
    transactions_count: int = Field(..., ge=0, description="Transaction count")
    avg_amount: float = Field(..., ge=0, description="Average transaction amount")
    fraudulent: bool = Field(..., description="Has fraudulent transactions")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "id": "C1231006815",
                "transactions_count": 58,
                "avg_amount": 205.33,
                "fraudulent": False
            }
        }


class TopCustomer(BaseModel):
    """Top customer model with volume statistics.

    Attributes
    ----------
    id : str
        Unique customer identifier.
    transactions_count : int
        Total number of transactions.
    total_amount : float
        Total transaction volume.
    avg_amount : float
        Average transaction amount.
    """

    id: str = Field(..., description="Customer identifier")
    transactions_count: int = Field(..., ge=0, description="Transaction count")
    total_amount: float = Field(..., ge=0, description="Total transaction volume")
    avg_amount: float = Field(..., ge=0, description="Average transaction amount")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "id": "C1231006815",
                "transactions_count": 150,
                "total_amount": 1500000.0,
                "avg_amount": 10000.0
            }
        }
