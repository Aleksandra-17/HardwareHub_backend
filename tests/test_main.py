"""Tests for main app."""


from src.main import app


class TestApp:
    """Test FastAPI app."""

    def test_app_exists(self):
        """App instance exists."""
        assert app is not None

    def test_app_title(self):
        """App has title."""
        assert hasattr(app, "title")

    def test_openapi_available(self, client):
        """OpenAPI schema is available."""
        response = client.get("/api/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data

    def test_docs_requires_auth(self, client):
        """Docs endpoint requires authentication."""
        response = client.get("/api/docs")
        assert response.status_code == 401

    def test_docs_with_auth(self, client):
        """Docs endpoint returns 200 with valid credentials."""
        response = client.get(
            "/api/docs",
            auth=("USERNAME", "PASSWORD"),
        )
        assert response.status_code == 200
