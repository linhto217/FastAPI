"""Tests for fraud detection routes (Routes 13-15)."""
import pytest
from fastapi.testclient import TestClient


class TestFraudRoutes:
    """Test cases for fraud detection endpoints."""

    def test_get_fraud_summary(self, client: TestClient) -> None:
        """Test GET /api/fraud/summary returns fraud overview."""
        response = client.get("/api/fraud/summary")
        assert response.status_code == 200

        data = response.json()
        assert "total_frauds" in data
        assert "flagged" in data
        assert "precision" in data
        assert "recall" in data

        assert data["total_frauds"] >= 0
        assert data["flagged"] >= 0
        assert 0 <= data["precision"] <= 1
        assert 0 <= data["recall"] <= 1

    def test_get_fraud_by_type(self, client: TestClient) -> None:
        """Test GET /api/fraud/by-type returns fraud rates per type."""
        response = client.get("/api/fraud/by-type")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        for type_fraud in data:
            assert "type" in type_fraud
            assert "total" in type_fraud
            assert "fraud_count" in type_fraud
            assert "fraud_rate" in type_fraud

            assert type_fraud["total"] >= 0
            assert type_fraud["fraud_count"] >= 0
            assert 0 <= type_fraud["fraud_rate"] <= 1

            # fraud_count should not exceed total
            assert type_fraud["fraud_count"] <= type_fraud["total"]

    def test_predict_fraud_legitimate(self, client: TestClient) -> None:
        """Test POST /api/fraud/predict for legitimate transaction."""
        request_data = {
            "type": "PAYMENT",
            "amount": 500.0,
            "oldbalanceOrg": 5000.0,
            "newbalanceOrig": 4500.0
        }

        response = client.post("/api/fraud/predict", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "isFraud" in data
        assert "probability" in data
        assert isinstance(data["isFraud"], bool)
        assert 0 <= data["probability"] <= 1

    def test_predict_fraud_suspicious(self, client: TestClient) -> None:
        """Test POST /api/fraud/predict for suspicious transaction."""
        # This transaction has multiple fraud indicators:
        # - High amount (>100k)
        # - Risky type (TRANSFER)
        # - Balance inconsistency
        request_data = {
            "type": "TRANSFER",
            "amount": 250000.0,
            "oldbalanceOrg": 300000.0,
            "newbalanceOrig": 0.0  # Inconsistent: should be 50000
        }

        response = client.post("/api/fraud/predict", json=request_data)
        assert response.status_code == 200

        data = response.json()
        # With balance inconsistency (+0.3), risky type (+0.3), high amount (+0.4)
        # Total score should be > 0.5, flagging as fraud
        assert data["isFraud"] is True
        assert data["probability"] > 0.5

    def test_predict_fraud_balance_inconsistency(
        self, client: TestClient
    ) -> None:
        """Test fraud prediction detects balance inconsistency."""
        request_data = {
            "type": "PAYMENT",
            "amount": 1000.0,
            "oldbalanceOrg": 5000.0,
            "newbalanceOrig": 3000.0  # Should be 4000
        }

        response = client.post("/api/fraud/predict", json=request_data)
        assert response.status_code == 200

        data = response.json()
        # Balance inconsistency should add to the score
        assert data["probability"] > 0

    def test_predict_fraud_high_amount(self, client: TestClient) -> None:
        """Test fraud prediction flags high amount transactions."""
        request_data = {
            "type": "TRANSFER",
            "amount": 150000.0,
            "oldbalanceOrg": 200000.0,
            "newbalanceOrig": 50000.0
        }

        response = client.post("/api/fraud/predict", json=request_data)
        assert response.status_code == 200

        data = response.json()
        # High amount (+0.4) + risky type (+0.3) = 0.7 > 0.5
        assert data["isFraud"] is True

    def test_predict_fraud_cash_out(self, client: TestClient) -> None:
        """Test fraud prediction for CASH_OUT type."""
        request_data = {
            "type": "CASH_OUT",
            "amount": 50000.0,
            "oldbalanceOrg": 50000.0,
            "newbalanceOrig": 0.0
        }

        response = client.post("/api/fraud/predict", json=request_data)
        assert response.status_code == 200

        data = response.json()
        # CASH_OUT is a risky type
        assert data["probability"] > 0

    def test_predict_fraud_with_customer_info(self, client: TestClient) -> None:
        """Test fraud prediction with customer ID for rapid transaction check."""
        request_data = {
            "type": "TRANSFER",
            "amount": 10000.0,
            "oldbalanceOrg": 50000.0,
            "newbalanceOrig": 40000.0,
            "nameOrig": "C1231006815",
            "step": 1
        }

        response = client.post("/api/fraud/predict", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "isFraud" in data
        assert "probability" in data

    def test_fraud_summary_consistency(self, client: TestClient) -> None:
        """Test fraud summary is consistent with fraud by type."""
        summary_response = client.get("/api/fraud/summary")
        by_type_response = client.get("/api/fraud/by-type")

        summary = summary_response.json()
        by_type = by_type_response.json()

        # Total frauds should match sum of fraud_count across types
        total_from_types = sum(t["fraud_count"] for t in by_type)
        assert total_from_types == summary["total_frauds"]

    def test_predict_fraud_invalid_request(self, client: TestClient) -> None:
        """Test fraud prediction with invalid request data."""
        # Missing required field
        request_data = {
            "type": "TRANSFER",
            "amount": 1000.0
            # Missing oldbalanceOrg and newbalanceOrig
        }

        response = client.post("/api/fraud/predict", json=request_data)
        assert response.status_code == 422  # Validation error
