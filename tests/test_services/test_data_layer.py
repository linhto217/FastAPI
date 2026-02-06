"""Tests for data access layer."""
import pytest
import pandas as pd

from banking_api.data.dataframe_dal import DataFrameDAL
from banking_api.data.loader import (
    REQUIRED_COLUMNS,
    VALID_TYPES,
    generate_transaction_ids,
    validate_columns,
    validate_fraud_values,
    validate_null_values,
    validate_types,
)


class TestDataLoader:
    """Test cases for data loader validation functions."""

    def test_required_columns_defined(self) -> None:
        """Test all required columns are defined."""
        expected_columns = {
            "step", "type", "amount", "nameOrig", "oldbalanceOrg",
            "newbalanceOrig", "nameDest", "oldbalanceDest",
            "newbalanceDest", "isFraud", "isFlaggedFraud"
        }
        assert set(REQUIRED_COLUMNS.keys()) == expected_columns

    def test_valid_types_defined(self) -> None:
        """Test valid transaction types are defined."""
        expected_types = {"CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"}
        assert VALID_TYPES == expected_types

    def test_validate_columns_success(self) -> None:
        """Test column validation passes with all columns."""
        data = {col: [1] for col in REQUIRED_COLUMNS}
        df = pd.DataFrame(data)

        missing = validate_columns(df)
        assert missing == []

    def test_validate_columns_missing(self) -> None:
        """Test column validation detects missing columns."""
        data = {"step": [1], "type": ["PAYMENT"]}
        df = pd.DataFrame(data)

        missing = validate_columns(df)
        assert len(missing) > 0
        assert "amount" in missing

    def test_validate_fraud_values_valid(self) -> None:
        """Test fraud validation passes with 0/1 values."""
        df = pd.DataFrame({"isFraud": [0, 1, 0, 1, 0]})
        invalid = validate_fraud_values(df)
        assert invalid == []

    def test_validate_fraud_values_invalid(self) -> None:
        """Test fraud validation detects invalid values."""
        df = pd.DataFrame({"isFraud": [0, 1, 2, 0, -1]})
        invalid = validate_fraud_values(df)
        assert len(invalid) == 2
        assert 2 in invalid
        assert 4 in invalid

    def test_validate_types_valid(self) -> None:
        """Test type validation passes with valid types."""
        df = pd.DataFrame({"type": ["PAYMENT", "TRANSFER", "CASH_OUT"]})
        invalid = validate_types(df)
        assert invalid == []

    def test_validate_types_invalid(self) -> None:
        """Test type validation detects invalid types."""
        df = pd.DataFrame({"type": ["PAYMENT", "INVALID_TYPE", "CASH_OUT"]})
        invalid = validate_types(df)
        assert "INVALID_TYPE" in invalid

    def test_validate_null_values_none(self) -> None:
        """Test null validation passes with no nulls."""
        data = {col: [1, 2, 3] for col in REQUIRED_COLUMNS}
        data["type"] = ["PAYMENT", "TRANSFER", "CASH_OUT"]
        data["nameOrig"] = ["C001", "C002", "C003"]
        data["nameDest"] = ["M001", "M002", "M003"]
        df = pd.DataFrame(data)

        nulls = validate_null_values(df)
        assert nulls == {}

    def test_validate_null_values_found(self) -> None:
        """Test null validation detects null values."""
        data = {col: [1, None, 3] for col in REQUIRED_COLUMNS}
        data["type"] = ["PAYMENT", None, "CASH_OUT"]
        data["nameOrig"] = ["C001", "C002", "C003"]
        data["nameDest"] = ["M001", "M002", "M003"]
        df = pd.DataFrame(data)

        nulls = validate_null_values(df)
        assert len(nulls) > 0

    def test_generate_transaction_ids(self) -> None:
        """Test transaction ID generation."""
        df = pd.DataFrame({"col": [1, 2, 3]})
        result = generate_transaction_ids(df)

        assert "id" in result.columns
        assert result["id"].tolist() == [
            "tx_0000000", "tx_0000001", "tx_0000002"
        ]


class TestDataFrameDAL:
    """Test cases for DataFrame data access layer."""

    def test_get_all_transactions(self, test_dal: DataFrameDAL) -> None:
        """Test getting all transactions with pagination."""
        transactions, total = test_dal.get_all_transactions(page=1, limit=5)

        assert isinstance(transactions, list)
        assert len(transactions) <= 5
        assert total > 0

    def test_get_all_transactions_with_filters(
        self, test_dal: DataFrameDAL
    ) -> None:
        """Test getting transactions with filters."""
        filters = {"type": "PAYMENT"}
        transactions, _ = test_dal.get_all_transactions(
            page=1, limit=10, filters=filters
        )

        for tx in transactions:
            assert tx["type"] == "PAYMENT"

    def test_get_transaction_by_id(self, test_dal: DataFrameDAL) -> None:
        """Test getting transaction by ID."""
        transaction = test_dal.get_transaction_by_id("tx_0000000")

        assert transaction is not None
        assert transaction["id"] == "tx_0000000"

    def test_get_transaction_by_id_not_found(
        self, test_dal: DataFrameDAL
    ) -> None:
        """Test getting non-existent transaction."""
        transaction = test_dal.get_transaction_by_id("tx_nonexistent")
        assert transaction is None

    def test_search_transactions(self, test_dal: DataFrameDAL) -> None:
        """Test searching transactions."""
        criteria = {"type": "TRANSFER"}
        transactions = test_dal.search_transactions(criteria)

        assert isinstance(transactions, list)
        for tx in transactions:
            assert tx["type"] == "TRANSFER"

    def test_get_unique_types(self, test_dal: DataFrameDAL) -> None:
        """Test getting unique transaction types."""
        types = test_dal.get_unique_types()

        assert isinstance(types, list)
        assert len(types) > 0

    def test_get_recent_transactions(self, test_dal: DataFrameDAL) -> None:
        """Test getting recent transactions."""
        transactions = test_dal.get_recent_transactions(n=3)

        assert isinstance(transactions, list)
        assert len(transactions) <= 3

    def test_get_customer_stats(self, test_dal: DataFrameDAL) -> None:
        """Test getting customer statistics."""
        # Get a customer from the data
        customers, _ = test_dal.get_all_customers(page=1, limit=1)

        if customers:
            stats = test_dal.get_customer_stats(customers[0])
            assert stats is not None
            assert "transactions_count" in stats
            assert "avg_amount" in stats

    def test_get_top_customers(self, test_dal: DataFrameDAL) -> None:
        """Test getting top customers."""
        top = test_dal.get_top_customers(n=3)

        assert isinstance(top, list)
        assert len(top) <= 3

        # Verify sorted by total_amount descending
        if len(top) > 1:
            for i in range(len(top) - 1):
                assert top[i]["total_amount"] >= top[i + 1]["total_amount"]

    def test_get_dataframe(self, test_dal: DataFrameDAL) -> None:
        """Test getting underlying DataFrame."""
        df = test_dal.get_dataframe()

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_get_customer_timeline(self, test_dal: DataFrameDAL) -> None:
        """Test getting customer transaction timeline."""
        customers, _ = test_dal.get_all_customers(page=1, limit=1)

        if customers:
            timeline = test_dal.get_customer_timeline(customers[0])
            assert isinstance(timeline, list)

            # Timeline should be sorted by step
            if len(timeline) > 1:
                for i in range(len(timeline) - 1):
                    assert timeline[i][0] <= timeline[i + 1][0]
