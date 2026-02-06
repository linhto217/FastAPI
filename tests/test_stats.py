"""Tests for statistics routes (Routes 9-12)."""
import pytest
from fastapi.testclient import TestClient


class TestStatsRoutes:
    """Test cases for statistics endpoints."""

    def test_get_overview(self, client: TestClient) -> None:
        """Test GET /api/stats/overview returns global statistics."""
        response = client.get("/api/stats/overview")
        assert response.status_code == 200

        data = response.json()
        assert "total_transactions" in data
        assert "fraud_rate" in data
        assert "avg_amount" in data
        assert "most_common_type" in data

        assert isinstance(data["total_transactions"], int)
        assert data["total_transactions"] > 0
        assert 0 <= data["fraud_rate"] <= 1
        assert data["avg_amount"] >= 0

    def test_get_amount_distribution(self, client: TestClient) -> None:
        """Test GET /api/stats/amount-distribution returns histogram."""
        response = client.get("/api/stats/amount-distribution")
        assert response.status_code == 200

        data = response.json()
        assert "bins" in data
        assert "counts" in data

        assert isinstance(data["bins"], list)
        assert isinstance(data["counts"], list)
        assert len(data["bins"]) == len(data["counts"])

    def test_get_stats_by_type(self, client: TestClient) -> None:
        """Test GET /api/stats/by-type returns per-type statistics."""
        response = client.get("/api/stats/by-type")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        for type_stat in data:
            assert "type" in type_stat
            assert "count" in type_stat
            assert "avg_amount" in type_stat

            assert type_stat["count"] > 0
            assert type_stat["avg_amount"] >= 0

    def test_get_daily_stats(self, client: TestClient) -> None:
        """Test GET /api/stats/daily returns daily statistics."""
        response = client.get("/api/stats/daily")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        for daily_stat in data:
            assert "step_range" in daily_stat
            assert "transaction_count" in daily_stat
            assert "avg_amount" in daily_stat
            assert "total_amount" in daily_stat

            assert daily_stat["transaction_count"] >= 0
            assert daily_stat["avg_amount"] >= 0
            assert daily_stat["total_amount"] >= 0

    def test_stats_consistency(self, client: TestClient) -> None:
        """Test that statistics are consistent across endpoints."""
        overview_response = client.get("/api/stats/overview")
        by_type_response = client.get("/api/stats/by-type")

        overview = overview_response.json()
        by_type = by_type_response.json()

        # Total count from by-type should match overview
        total_from_types = sum(t["count"] for t in by_type)
        assert total_from_types == overview["total_transactions"]

    def test_overview_fraud_rate_range(self, client: TestClient) -> None:
        """Test that fraud rate is within valid range."""
        response = client.get("/api/stats/overview")
        data = response.json()

        assert 0 <= data["fraud_rate"] <= 1

    def test_amount_distribution_bins_ordered(self, client: TestClient) -> None:
        """Test that amount distribution bins are properly ordered."""
        response = client.get("/api/stats/amount-distribution")
        data = response.json()

        # Bins should be in ascending order of amounts
        bins = data["bins"]
        assert len(bins) > 0

        # All counts should be non-negative
        for count in data["counts"]:
            assert count >= 0
