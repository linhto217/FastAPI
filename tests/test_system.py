"""Tests for system routes (Routes 19-20)."""
import pytest
from fastapi.testclient import TestClient


class TestSystemRoutes:
    """Test cases for system endpoints."""

    def test_health_check(self, client: TestClient) -> None:
        """Test GET /api/system/health returns health status."""
        response = client.get("/api/system/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "uptime" in data
        assert "dataset_loaded" in data

        assert data["status"] == "ok"
        assert data["dataset_loaded"] is True

    def test_health_check_uptime_format(self, client: TestClient) -> None:
        """Test health check uptime is in expected format."""
        response = client.get("/api/system/health")
        data = response.json()

        uptime = data["uptime"]
        # Uptime should be a string like "Xh Xmin" or "Xmin Xs" or "Xs"
        assert isinstance(uptime, str)
        assert len(uptime) > 0

    def test_get_metadata(self, client: TestClient) -> None:
        """Test GET /api/system/metadata returns service metadata."""
        response = client.get("/api/system/metadata")
        assert response.status_code == 200

        data = response.json()
        assert "version" in data
        assert "last_update" in data
        assert "test_mode" in data
        assert "total_transactions" in data

        # Version should be semantic version format
        assert data["version"] == "1.0.0"

        # Test mode should be True (we're running tests)
        assert data["test_mode"] is True

        # Total transactions should be positive
        assert data["total_transactions"] > 0

    def test_metadata_last_update_format(self, client: TestClient) -> None:
        """Test metadata last_update is valid ISO timestamp."""
        response = client.get("/api/system/metadata")
        data = response.json()

        last_update = data["last_update"]
        # Should be ISO format string
        assert isinstance(last_update, str)
        assert "T" in last_update  # ISO format contains T separator

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test GET / returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "docs" in data
        assert "redoc" in data

        assert data["docs"] == "/docs"
        assert data["redoc"] == "/redoc"

    def test_docs_endpoint(self, client: TestClient) -> None:
        """Test Swagger UI documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_endpoint(self, client: TestClient) -> None:
        """Test ReDoc documentation is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_schema(self, client: TestClient) -> None:
        """Test OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

        # Check API info
        assert schema["info"]["title"] == "Banking Transactions API"
        assert schema["info"]["version"] == "1.0.0"

    def test_health_dataset_loaded(self, client: TestClient) -> None:
        """Test health check correctly reports dataset status."""
        # First check health
        health_response = client.get("/api/system/health")
        health_data = health_response.json()

        # Then verify with metadata
        metadata_response = client.get("/api/system/metadata")
        metadata_data = metadata_response.json()

        # If dataset is loaded, total_transactions should be > 0
        if health_data["dataset_loaded"]:
            assert metadata_data["total_transactions"] > 0

    def test_system_endpoints_performance(self, client: TestClient) -> None:
        """Test system endpoints respond quickly."""
        import time

        # Health check should be fast
        start = time.time()
        response = client.get("/api/system/health")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.5  # Should respond in under 500ms

        # Metadata should also be fast
        start = time.time()
        response = client.get("/api/system/metadata")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.5
