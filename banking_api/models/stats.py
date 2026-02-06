"""Statistics Pydantic models.

This module defines the schemas for statistical data responses.
"""
from pydantic import BaseModel, Field


class StatsOverview(BaseModel):
    """Global dataset statistics model.

    Attributes
    ----------
    total_transactions : int
        Total number of transactions in the dataset.
    fraud_rate : float
        Percentage of fraudulent transactions.
    avg_amount : float
        Average transaction amount.
    most_common_type : str
        Most frequently occurring transaction type.
    """

    total_transactions: int = Field(..., ge=0, description="Total transactions")
    fraud_rate: float = Field(..., ge=0, le=1, description="Fraud rate")
    avg_amount: float = Field(..., ge=0, description="Average amount")
    most_common_type: str = Field(..., description="Most common type")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "total_transactions": 6362620,
                "fraud_rate": 0.00129,
                "avg_amount": 178642.15,
                "most_common_type": "CASH_OUT"
            }
        }


class AmountDistribution(BaseModel):
    """Amount distribution histogram model.

    Attributes
    ----------
    bins : list[str]
        Bin labels for the histogram.
    counts : list[int]
        Count of transactions in each bin.
    """

    bins: list[str] = Field(..., description="Histogram bin labels")
    counts: list[int] = Field(..., description="Transaction counts per bin")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "bins": ["0-100", "100-500", "500-1000", "1000-5000"],
                "counts": [10000, 53000, 42000, 21000]
            }
        }


class TypeStats(BaseModel):
    """Statistics per transaction type model.

    Attributes
    ----------
    type : str
        Transaction type.
    count : int
        Total transactions of this type.
    avg_amount : float
        Average amount for this type.
    total_amount : float
        Total amount for this type.
    """

    type: str = Field(..., description="Transaction type")
    count: int = Field(..., ge=0, description="Transaction count")
    avg_amount: float = Field(..., ge=0, description="Average amount")
    total_amount: float = Field(..., ge=0, description="Total amount")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "type": "PAYMENT",
                "count": 1250000,
                "avg_amount": 350.21,
                "total_amount": 437762500.0
            }
        }


class DailyStats(BaseModel):
    """Daily transaction statistics model.

    Attributes
    ----------
    step_range : str
        Time step range (representing a day).
    transaction_count : int
        Number of transactions in this period.
    avg_amount : float
        Average transaction amount.
    total_amount : float
        Total transaction amount.
    """

    step_range: str = Field(..., description="Step range (day)")
    transaction_count: int = Field(..., ge=0, description="Transaction count")
    avg_amount: float = Field(..., ge=0, description="Average amount")
    total_amount: float = Field(..., ge=0, description="Total amount")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "step_range": "1-24",
                "transaction_count": 212000,
                "avg_amount": 175000.50,
                "total_amount": 37100106000.0
            }
        }
