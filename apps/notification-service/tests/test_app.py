from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "notification-service"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text


def test_create_notification():
    data = {"type": "email", "message": "Order confirmed", "recipient": "user@example.com"}
    response = client.post("/notifications", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["type"] == "email"
    assert result["status"] == "sent"
    assert result["message"] == "Order confirmed"


def test_get_notifications():
    response = client.get("/notifications")
    assert response.status_code == 200
    data = response.json()
    assert "notifications" in data
    assert "count" in data
    assert data["count"] >= 1
