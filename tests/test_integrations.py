import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient

from app.main import app
from app.services import stripe_gateway
from app.services.store import event_store

client = TestClient(app)


def setup_function() -> None:
    event_store.clear()


def _make_signature(payload: dict, secret: str) -> tuple[str, bytes]:
    timestamp = int(time.time())
    raw_body = json.dumps(payload).encode("utf-8")
    signed_payload = f"{timestamp}.".encode("utf-8") + raw_body
    signature = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={signature}", raw_body


def test_home_page() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Stripe Test Mode" in response.text or "Test mode only" in response.text
    assert "Create demo order" in response.text


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_order_event() -> None:
    payload = {
        "source": "demo_store",
        "order_id": "DEMO-1001",
        "customer_name": "Alex Chen",
        "customer_email": "alex@example.com",
        "amount": 499,
        "currency": "usd",
    }

    response = client.post("/api/integrations/orders", json=payload)
    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "pending_payment"
    assert body["target_system"] == "stripe_checkout"
    assert body["mapped_payload"]["external_order_id"] == "DEMO-1001"


def test_create_checkout_session_updates_event(monkeypatch) -> None:
    create_payload = {
        "source": "demo_store",
        "order_id": "DEMO-1001",
        "customer_name": "Alex Chen",
        "customer_email": "alex@example.com",
        "amount": 499,
        "currency": "usd",
    }
    create_response = client.post("/api/integrations/orders", json=create_payload)
    event_id = create_response.json()["event_id"]

    def fake_create_checkout_session(event):
        assert event.event_id == event_id
        return {"id": "cs_test_123", "url": "https://checkout.stripe.com/pay/cs_test_123"}

    monkeypatch.setattr(stripe_gateway, "create_checkout_session", fake_create_checkout_session)
    from app.services import processor
    monkeypatch.setattr(processor, "create_checkout_session", fake_create_checkout_session)

    response = client.post("/api/payments/checkout-session", json={"event_id": event_id})

    assert response.status_code == 200
    assert response.json()["status"] == "checkout_created"
    assert response.json()["checkout_session_id"] == "cs_test_123"

    event_response = client.get(f"/api/integrations/events/{event_id}")
    assert event_response.json()["status"] == "checkout_created"


def test_stripe_webhook_updates_event_status() -> None:
    create_payload = {
        "source": "demo_store",
        "order_id": "DEMO-1001",
        "customer_name": "Alex Chen",
        "customer_email": "alex@example.com",
        "amount": 499,
        "currency": "usd",
    }
    create_response = client.post("/api/integrations/orders", json=create_payload)
    event_id = create_response.json()["event_id"]

    webhook_payload = {
        "id": "evt_test_123",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "client_reference_id": event_id,
                "payment_intent": "pi_test_123",
                "metadata": {"event_id": event_id},
            }
        },
    }
    signature, raw_body = _make_signature(webhook_payload, "whsec_test_secret")

    response = client.post(
        "/api/integrations/webhooks/stripe",
        content=raw_body,
        headers={"Stripe-Signature": signature, "Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "payment_received"

    event_response = client.get(f"/api/integrations/events/{event_id}")
    assert event_response.status_code == 200
    assert event_response.json()["status"] == "payment_received"
    assert event_response.json()["stripe_checkout_session_id"] == "cs_test_123"


def test_invalid_order_payload_returns_422() -> None:
    invalid_payload = {
        "source": "s",
        "order_id": "1",
        "customer_name": "A",
        "customer_email": "not-an-email",
        "amount": 0,
        "currency": "us",
    }

    response = client.post("/api/integrations/orders", json=invalid_payload)

    assert response.status_code == 422


def test_checkout_for_missing_event_returns_404() -> None:
    response = client.post("/api/payments/checkout-session", json={"event_id": "evt_9999"})

    assert response.status_code == 404
