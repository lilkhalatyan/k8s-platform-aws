from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "order-service"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text


def test_create_and_get_order():
    order_data = {"items": ["laptop", "mouse"], "total": 1299.99, "customer": "jane"}
    response = client.post("/orders", json=order_data)
    assert response.status_code == 200
    created = response.json()
    assert created["status"] == "created"
    assert created["customer"] == "jane"

    order_id = created["id"]
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_get_orders_list():
    response = client.get("/orders")
    assert response.status_code == 200
    assert "orders" in response.json()
    assert "count" in response.json()


def test_get_order_not_found():
    response = client.get("/orders/nonexistent-id")
    assert response.status_code == 404
