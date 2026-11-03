"""Unit tests for FastAPI health check, static web interface, and core endpoints."""


def test_health_check_endpoint(client):
    """Verify GET /api/v1/health returns exact required JSON payload."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "HireAI" in data["application"]


def test_docs_available(client):
    """Verify OpenAPI Swagger documentation endpoint is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_root_serves_interactive_dashboard(client):
    """Verify root endpoint serves interactive HTML dashboard featuring robotics logo."""
    response = client.get("/")
    assert response.status_code == 200
    assert "HireAI" in response.text
    assert "robotics_resume_robo.jpg" in response.text


def test_static_robo_logo_accessible(client):
    """Verify high-resolution robotics logo asset is served correctly."""
    response = client.get("/static/robotics_resume_robo.jpg")
    assert response.status_code == 200
    assert len(response.content) > 10000


def test_404_error_handling(client):
    """Verify centralized exception handler catches non-existent endpoints gracefully."""
    response = client.get("/api/v1/non_existent_route")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
    assert data["error_type"] == "http_error"
