"""Tests for transaction routes (Routes 1-8)."""
import pytest
from fastapi.testclient import TestClient


class TestTransactionRoutes:
    """Test cases for transaction endpoints."""

    def test_list_transactions(self, client: TestClient) -> None:
        """Test GET /api/transactions returns paginated transactions."""
        response = client.get("/api/transactions?page=1&limit=10")
        assert response.status_code == 200

        data = response.json()
        assert "page" in data
        assert "transactions" in data
        assert data["page"] == 1
        assert isinstance(data["transactions"], list)

    def test_list_transactions_with_filters(self, client: TestClient) -> None:
        """Test GET /api/transactions with type filter."""
        response = client.get("/api/transactions?type=PAYMENT")
        assert response.status_code == 200

        data = response.json()
        for tx in data["transactions"]:
            assert tx["type"] == "PAYMENT"

    def test_list_transactions_with_amount_filter(self, client: TestClient) -> None:
        """Test GET /api/transactions with amount range filter."""
        response = client.get(
            "/api/transactions?min_amount=1000&max_amount=50000"
        )
        assert response.status_code == 200

        data = response.json()
        for tx in data["transactions"]:
            assert 1000 <= tx["amount"] <= 50000

    def test_get_transaction_by_id(self, client: TestClient) -> None:
        """Test GET /api/transactions/{id} returns transaction details."""
        response = client.get("/api/transactions/tx_0000000")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == "tx_0000000"
        assert "amount" in data
        assert "type" in data

    def test_get_transaction_not_found(self, client: TestClient) -> None:
        """Test GET /api/transactions/{id} returns 404 for invalid ID."""
        response = client.get("/api/transactions/tx_nonexistent")
        assert response.status_code == 404

    def test_search_transactions(self, client: TestClient) -> None:
        """Test POST /api/transactions/search with criteria."""
        criteria = {
            "type": "TRANSFER",
            "isFraud": 1
        }
        response = client.post("/api/transactions/search", json=criteria)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        for tx in data:
            assert tx["type"] == "TRANSFER"
            assert tx["isFraud"] == 1

    def test_search_transactions_with_amount_range(
        self, client: TestClient
    ) -> None:
        """Test POST /api/transactions/search with amount range."""
        criteria = {
            "amount_range": [10000, 100000]
        }
        response = client.post("/api/transactions/search", json=criteria)
        assert response.status_code == 200

        data = response.json()
        for tx in data:
            assert 10000 <= tx["amount"] <= 100000

    def test_get_transaction_types(self, client: TestClient) -> None:
        """Test GET /api/transactions/types returns unique types."""
        response = client.get("/api/transactions/types")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check known types exist
        expected_types = {"PAYMENT", "TRANSFER", "CASH_OUT", "CASH_IN", "DEBIT"}
        assert set(data).issubset(expected_types)

    def test_get_recent_transactions(self, client: TestClient) -> None:
        """Test GET /api/transactions/recent returns recent transactions."""
        response = client.get("/api/transactions/recent?n=5")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_transactions_by_customer(self, client: TestClient) -> None:
        """Test GET /api/transactions/by-customer/{customer_id}."""
        # Use a customer ID from test data
        response = client.get("/api/transactions/by-customer/C1231006815")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        for tx in data:
            assert tx["nameOrig"] == "C1231006815"

    def test_get_transactions_to_customer(self, client: TestClient) -> None:
        """Test GET /api/transactions/to-customer/{customer_id}."""
        response = client.get("/api/transactions/to-customer/M1979787155")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        for tx in data:
            assert tx["nameDest"] == "M1979787155"

    def test_delete_transaction_in_test_mode(self, client: TestClient) -> None:
        """Test DELETE /api/transactions/{id} in test mode."""
        # First get a transaction that exists
        response = client.get("/api/transactions?limit=1")
        data = response.json()

        if data["transactions"]:
            tx_id = data["transactions"][0]["id"]
            delete_response = client.delete(f"/api/transactions/{tx_id}")
            assert delete_response.status_code == 200

            result = delete_response.json()
            assert result["success"] is True

    def test_delete_nonexistent_transaction(self, client: TestClient) -> None:
        """Test DELETE /api/transactions/{id} for nonexistent ID."""
        response = client.delete("/api/transactions/tx_nonexistent")
        assert response.status_code == 404
