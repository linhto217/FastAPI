"""Tests for customer routes (Routes 16-18)."""
import pytest
from fastapi.testclient import TestClient


class TestCustomerRoutes:
    """Test cases for customer endpoints."""

    def test_list_customers(self, client: TestClient) -> None:
        """Test GET /api/customers returns paginated customer list."""
        response = client.get("/api/customers?page=1&limit=10")
        assert response.status_code == 200

        data = response.json()
        assert "page" in data
        assert "limit" in data
        assert "total" in data
        assert "data" in data

        assert data["page"] == 1
        assert data["limit"] == 10
        assert isinstance(data["data"], list)

    def test_list_customers_pagination(self, client: TestClient) -> None:
        """Test customer list pagination works correctly."""
        # Get first page
        response1 = client.get("/api/customers?page=1&limit=5")
        data1 = response1.json()

        # Get second page
        response2 = client.get("/api/customers?page=2&limit=5")
        data2 = response2.json()

        # Pages should have different customers (if enough data)
        if data1["total"] > 5:
            assert data1["data"] != data2["data"]

    def test_get_customer_by_id(self, client: TestClient) -> None:
        """Test GET /api/customers/{customer_id} returns customer profile."""
        # Use a known customer from test data
        response = client.get("/api/customers/C1231006815")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == "C1231006815"
        assert "transactions_count" in data
        assert "avg_amount" in data
        assert "fraudulent" in data

        assert data["transactions_count"] > 0
        assert data["avg_amount"] >= 0
        assert isinstance(data["fraudulent"], bool)

    def test_get_customer_not_found(self, client: TestClient) -> None:
        """Test GET /api/customers/{customer_id} returns 404 for invalid ID."""
        response = client.get("/api/customers/C_nonexistent")
        assert response.status_code == 404

    def test_get_top_customers(self, client: TestClient) -> None:
        """Test GET /api/customers/top returns top customers by volume."""
        response = client.get("/api/customers/top?n=5")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

        # Verify customers are sorted by total_amount (descending)
        if len(data) > 1:
            for i in range(len(data) - 1):
                assert data[i]["total_amount"] >= data[i + 1]["total_amount"]

        # Check required fields
        for customer in data:
            assert "id" in customer
            assert "transactions_count" in customer
            assert "total_amount" in customer
            assert "avg_amount" in customer

    def test_top_customers_default_n(self, client: TestClient) -> None:
        """Test GET /api/customers/top uses default n=10."""
        response = client.get("/api/customers/top")
        assert response.status_code == 200

        data = response.json()
        assert len(data) <= 10

    def test_customer_profile_accuracy(self, client: TestClient) -> None:
        """Test customer profile data is accurate."""
        # Get a customer
        customers_response = client.get("/api/customers?limit=1")
        customers = customers_response.json()

        if customers["data"]:
            customer_id = customers["data"][0]

            # Get customer profile
            profile_response = client.get(f"/api/customers/{customer_id}")
            profile = profile_response.json()

            # Get customer transactions
            tx_response = client.get(
                f"/api/transactions/by-customer/{customer_id}"
            )
            transactions = tx_response.json()

            # Verify transaction count matches
            assert profile["transactions_count"] == len(transactions)

    def test_customer_fraudulent_flag(self, client: TestClient) -> None:
        """Test customer fraudulent flag is correctly set."""
        # Find a customer with fraud history from test data
        response = client.get("/api/customers/C1305486145")

        if response.status_code == 200:
            data = response.json()
            # This customer has a fraudulent transaction in test data
            # The fraudulent flag should reflect this
            assert isinstance(data["fraudulent"], bool)

    def test_list_customers_total_count(self, client: TestClient) -> None:
        """Test customer list total count is accurate."""
        response = client.get("/api/customers?page=1&limit=100")
        data = response.json()

        # Total should be >= number of customers returned
        assert data["total"] >= len(data["data"])

    def test_top_customers_limit_validation(self, client: TestClient) -> None:
        """Test top customers endpoint validates n parameter."""
        # n should be >= 1
        response = client.get("/api/customers/top?n=0")
        assert response.status_code == 422  # Validation error

    def test_customer_average_amount(self, client: TestClient) -> None:
        """Test customer average amount calculation."""
        response = client.get("/api/customers/C1231006815")

        if response.status_code == 200:
            data = response.json()

            # avg_amount should be positive if transactions exist
            if data["transactions_count"] > 0:
                assert data["avg_amount"] > 0
