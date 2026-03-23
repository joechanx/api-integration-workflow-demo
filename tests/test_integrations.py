from fastapi.testclient import TestClient

from app.main import app
from app.services.ecpay_checkmac import generate_check_mac_value
from app.services.store import event_store

client = TestClient(app)


def setup_function() -> None:
    event_store.clear()


def test_home_page() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "ECPay stage" in response.text
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
        "currency": "TWD",
    }

    response = client.post("/api/integrations/orders", json=payload)
    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "pending_payment"
    assert body["target_system"] == "ecpay_stage_credit"
    assert body["mapped_payload"]["external_order_id"] == "DEMO-1001"


def test_prepare_checkout_updates_event() -> None:
    create_payload = {
        "source": "demo_store",
        "order_id": "DEMO-1001",
        "customer_name": "Alex Chen",
        "customer_email": "alex@example.com",
        "amount": 499,
        "currency": "TWD",
    }
    create_response = client.post("/api/integrations/orders", json=create_payload)
    event_id = create_response.json()["event_id"]

    response = client.post("/api/payments/ecpay/checkout", json={"event_id": event_id})

    assert response.status_code == 200
    assert response.json()["status"] == "redirect_ready"
    assert response.json()["merchant_trade_no"].startswith("DEMO")
    assert response.json()["payment_page_url"] == f"/payments/ecpay/redirect/{event_id}"

    event_response = client.get(f"/api/integrations/events/{event_id}")
    assert event_response.json()["status"] == "redirect_ready"


def test_ecpay_return_updates_event_status() -> None:
    create_payload = {
        "source": "demo_store",
        "order_id": "DEMO-1001",
        "customer_name": "Alex Chen",
        "customer_email": "alex@example.com",
        "amount": 499,
        "currency": "TWD",
    }
    create_response = client.post("/api/integrations/orders", json=create_payload)
    event_id = create_response.json()["event_id"]
    checkout_response = client.post("/api/payments/ecpay/checkout", json={"event_id": event_id})
    merchant_trade_no = checkout_response.json()["merchant_trade_no"]

    form_payload = {
        "MerchantID": "3002607",
        "MerchantTradeNo": merchant_trade_no,
        "StoreID": "",
        "RtnCode": "1",
        "RtnMsg": "交易成功",
        "TradeNo": "241234567890",
        "TradeAmt": "499",
        "PaymentDate": "2026/03/24 12:00:00",
        "PaymentType": "Credit_CreditCard",
        "TradeDate": "2026/03/24 12:00:00",
        "SimulatePaid": "0",
        "CustomField1": event_id,
        "CustomField2": "DEMO-1001",
        "CustomField3": "alex@example.com",
        "CustomField4": "demo_store",
    }
    form_payload["CheckMacValue"] = generate_check_mac_value(form_payload)

    response = client.post("/api/integrations/webhooks/ecpay/return", data=form_payload)

    assert response.status_code == 200
    assert response.text == "1|OK"

    event_response = client.get(f"/api/integrations/events/{event_id}")
    assert event_response.status_code == 200
    assert event_response.json()["status"] == "paid"
    assert event_response.json()["ecpay_trade_no"] == "241234567890"


def test_invalid_order_payload_returns_422() -> None:
    invalid_payload = {
        "source": "s",
        "order_id": "1",
        "customer_name": "A",
        "customer_email": "not-an-email",
        "amount": 0,
        "currency": "USD",
    }

    response = client.post("/api/integrations/orders", json=invalid_payload)

    assert response.status_code == 422


def test_checkout_for_missing_event_returns_404() -> None:
    response = client.post("/api/payments/ecpay/checkout", json={"event_id": "evt_9999"})

    assert response.status_code == 404


def test_redirect_page_renders_form() -> None:
    create_payload = {
        "source": "demo_store",
        "order_id": "DEMO-1001",
        "customer_name": "Alex Chen",
        "customer_email": "alex@example.com",
        "amount": 499,
        "currency": "TWD",
    }
    create_response = client.post("/api/integrations/orders", json=create_payload)
    event_id = create_response.json()["event_id"]
    client.post("/api/payments/ecpay/checkout", json={"event_id": event_id})

    response = client.get(f"/payments/ecpay/redirect/{event_id}")

    assert response.status_code == 200
    assert "Redirecting to ECPay stage checkout" in response.text
    assert "Continue to ECPay stage checkout" in response.text
