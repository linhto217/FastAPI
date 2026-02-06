"""Tests for fraud detection service logic."""
import pytest
import pandas as pd

from banking_api.services.fraud_detection_service import (
    BALANCE_TOLERANCE,
    HIGH_AMOUNT_THRESHOLD,
    RAPID_TRANSACTION_STEP_GAP,
    RISKY_TYPES,
    compute_fraud_stats,
)


class TestFraudDetectionRules:
    """Test cases for fraud detection heuristic rules."""

    def test_risky_types_defined(self) -> None:
        """Test that risky transaction types are properly defined."""
        assert "CASH_OUT" in RISKY_TYPES
        assert "TRANSFER" in RISKY_TYPES
        assert "PAYMENT" not in RISKY_TYPES
        assert "CASH_IN" not in RISKY_TYPES

    def test_high_amount_threshold(self) -> None:
        """Test high amount threshold is 100,000."""
        assert HIGH_AMOUNT_THRESHOLD == 100000.0

    def test_balance_tolerance(self) -> None:
        """Test balance tolerance for inconsistency check."""
        assert BALANCE_TOLERANCE == 0.01

    def test_rapid_transaction_gap(self) -> None:
        """Test rapid transaction step gap is 1 hour."""
        assert RAPID_TRANSACTION_STEP_GAP == 1

    def test_compute_fraud_stats(self, sample_dataframe: pd.DataFrame) -> None:
        """Test fraud statistics computation."""
        stats = compute_fraud_stats(sample_dataframe)

        assert "fraud_summary" in stats
        assert "fraud_by_type" in stats

        summary = stats["fraud_summary"]
        assert "total_frauds" in summary
        assert "flagged" in summary
        assert "precision" in summary
        assert "recall" in summary

        # Verify fraud count matches DataFrame
        expected_frauds = sample_dataframe["isFraud"].sum()
        assert summary["total_frauds"] == expected_frauds

    def test_fraud_by_type_coverage(
        self, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test fraud by type covers all transaction types."""
        stats = compute_fraud_stats(sample_dataframe)

        fraud_types = {item["type"] for item in stats["fraud_by_type"]}
        df_types = set(sample_dataframe["type"].unique())

        assert fraud_types == df_types

    def test_fraud_rate_calculation(
        self, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test fraud rate is correctly calculated per type."""
        stats = compute_fraud_stats(sample_dataframe)

        for type_stat in stats["fraud_by_type"]:
            if type_stat["total"] > 0:
                expected_rate = type_stat["fraud_count"] / type_stat["total"]
                assert abs(type_stat["fraud_rate"] - expected_rate) < 0.0001


class TestFraudScoring:
    """Test cases for fraud scoring logic."""

    def test_balance_inconsistency_detection(self) -> None:
        """Test balance inconsistency is correctly detected."""
        # Consistent: 5000 - 1000 = 4000
        old_balance = 5000.0
        amount = 1000.0
        new_balance_consistent = 4000.0
        new_balance_inconsistent = 3000.0

        # Check consistency
        diff_consistent = abs(
            (old_balance - amount) - new_balance_consistent
        )
        diff_inconsistent = abs(
            (old_balance - amount) - new_balance_inconsistent
        )

        assert diff_consistent <= BALANCE_TOLERANCE
        assert diff_inconsistent > BALANCE_TOLERANCE

    def test_high_amount_detection(self) -> None:
        """Test high amount transactions are correctly flagged."""
        low_amount = 50000.0
        high_amount = 150000.0

        assert low_amount <= HIGH_AMOUNT_THRESHOLD
        assert high_amount > HIGH_AMOUNT_THRESHOLD

    def test_risky_type_detection(self) -> None:
        """Test risky transaction types are correctly identified."""
        assert "TRANSFER" in RISKY_TYPES
        assert "CASH_OUT" in RISKY_TYPES
        assert "PAYMENT" not in RISKY_TYPES
        assert "DEBIT" not in RISKY_TYPES
        assert "CASH_IN" not in RISKY_TYPES


class TestPrecisionRecall:
    """Test cases for precision and recall calculations."""

    def test_precision_recall_bounds(
        self, sample_dataframe: pd.DataFrame
    ) -> None:
        """Test precision and recall are within valid bounds."""
        stats = compute_fraud_stats(sample_dataframe)
        summary = stats["fraud_summary"]

        assert 0 <= summary["precision"] <= 1
        assert 0 <= summary["recall"] <= 1

    def test_precision_calculation(self) -> None:
        """Test precision calculation: flagged_and_fraud / flagged."""
        # Create test data
        data = {
            "isFraud": [1, 1, 0, 0, 1],
            "isFlaggedFraud": [1, 0, 1, 0, 1],
            "type": ["TRANSFER"] * 5,
            "amount": [1000] * 5,
        }
        df = pd.DataFrame(data)

        # Flagged and fraud: rows 0 and 4 = 2
        # Total flagged: rows 0, 2, 4 = 3
        # Precision = 2/3 = 0.67

        stats = compute_fraud_stats(df)
        expected_precision = 2 / 3
        assert abs(stats["fraud_summary"]["precision"] - expected_precision) < 0.01

    def test_recall_calculation(self) -> None:
        """Test recall calculation: flagged_and_fraud / total_frauds."""
        # Create test data
        data = {
            "isFraud": [1, 1, 0, 0, 1],
            "isFlaggedFraud": [1, 0, 1, 0, 1],
            "type": ["TRANSFER"] * 5,
            "amount": [1000] * 5,
        }
        df = pd.DataFrame(data)

        # Flagged and fraud: rows 0 and 4 = 2
        # Total fraud: rows 0, 1, 4 = 3
        # Recall = 2/3 = 0.67

        stats = compute_fraud_stats(df)
        expected_recall = 2 / 3
        assert abs(stats["fraud_summary"]["recall"] - expected_recall) < 0.01
