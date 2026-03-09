"""Tests for configuration (App)."""

from src.configuration.app import App


class TestApp:
    """Test App class."""

    def test_app_creates_fastapi(self):
        """App creates FastAPI instance."""
        app_instance = App()
        assert app_instance.app is not None

    def test_app_has_title(self):
        """App has title."""
        app_instance = App()
        assert hasattr(app_instance.app, "title")
        assert app_instance.app.title == "Api microservice"

    def test_app_has_routes(self):
        """App has API routes registered."""
        app_instance = App()
        path_strs = [getattr(r, "path", str(r)) for r in app_instance.app.routes]
        assert any("openapi" in p for p in path_strs)
