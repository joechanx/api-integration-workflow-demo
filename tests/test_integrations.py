from fastapi.testclient import TestClient

from app.main import app
from app.services.store import event_store

client = TestClient(app)


def setup_function() -> None:
    event_store.clear()


def test_home_page() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "API Integration Workflow Demo" in response.text
    assert "Swagger UI" in response.text


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_order_event() -> None:
    payload = {
        "source": "shopify",
        "order_id": "SHP-1001",
        "customer_name": "Alex Chen",
        "customer_email": "alex@example.com",
        "amount": 1299,
        "currency": "TWD",
    }

    response = client.post("/api/integrations/orders", json=payload)
    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "received"
    assert body["target_system"] == "mock_erp"
    assert body["mapped_payload"]["external_order_id"] == "SHP-1001"
    assert body["mapped_payload"]["client_name"] == "Alex Chen"


def test_apply_webhook_and_get_event_status() -> None:
    create_payload = {
        "source": "shopify",
        "order_id": "SHP-1001",
        "customer_name": "Alex Chen",
        "customer_email": "alex@example.com",
        "amount": 1299,
        "currency": "TWD",
    }
    create_response = client.post("/api/integrations/orders", json=create_payload)
    event_id = create_response.json()["event_id"]

    webhook_payload = {
        "event_id": event_id,
        "result": "processed",
        "reference_id": "ERP-2026-0001",
        "message": "Order synced successfully",
    }
    webhook_response = client.post("/api/integrations/webhooks/erp", json=webhook_payload)
    event_response = client.get(f"/api/integrations/events/{event_id}")

    assert webhook_response.status_code == 200
    assert webhook_response.json()["status"] == "processed"
    assert event_response.status_code == 200
    assert event_response.json()["status"] == "processed"
    assert event_response.json()["external_reference"] == "ERP-2026-0001"


def test_invalid_order_payload_returns_422() -> None:
    invalid_payload = {
        "source": "s",
        "order_id": "1",
        "customer_name": "A",
        "customer_email": "not-an-email",
        "amount": 0,
        "currency": "TW",
    }

    response = client.post("/api/integrations/orders", json=invalid_payload)

    assert response.status_code == 422


def test_webhook_for_missing_event_returns_404() -> None:
    payload = {
        "event_id": "evt_9999",
        "result": "failed",
        "message": "Event missing",
    }

    response = client.post("/api/integrations/webhooks/erp", json=payload)

    assert response.status_code == 404
