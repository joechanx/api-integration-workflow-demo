import hashlib
import hmac
import json
import time
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import PUBLIC_BASE_URL, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from app.models import EventRecord

STRIPE_API_BASE = "https://api.stripe.com"


class StripeGatewayError(Exception):
    pass


def _require_stripe_key() -> str:
    if not STRIPE_SECRET_KEY:
        raise StripeGatewayError("STRIPE_SECRET_KEY is not configured.")
    return STRIPE_SECRET_KEY


def _require_webhook_secret() -> str:
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="STRIPE_WEBHOOK_SECRET is not configured.",
        )
    return STRIPE_WEBHOOK_SECRET


def create_checkout_session(event: EventRecord) -> dict[str, Any]:
    secret_key = _require_stripe_key()
    success_url = f"{PUBLIC_BASE_URL}/payments/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{PUBLIC_BASE_URL}/payments/cancel?event_id={event.event_id}"

    form_data = {
        "mode": "payment",
        "client_reference_id": event.event_id,
        "customer_email": event.mapped_payload.client_email,
        "success_url": success_url,
        "cancel_url": cancel_url,
        "metadata[event_id]": event.event_id,
        "payment_intent_data[metadata][event_id]": event.event_id,
        "line_items[0][quantity]": "1",
        "line_items[0][price_data][currency]": event.mapped_payload.currency.lower(),
        "line_items[0][price_data][unit_amount]": str(event.mapped_payload.total_amount),
        "line_items[0][price_data][product_data][name]": f"Demo Order {event.mapped_payload.external_order_id}",
        "line_items[0][price_data][product_data][description]": "API Integration Workflow Demo",
    }

    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        response = client.post(
            f"{STRIPE_API_BASE}/v1/checkout/sessions",
            data=form_data,
            auth=(secret_key, ""),
            headers={"User-Agent": "api-integration-workflow-demo/1.0"},
        )

    if response.status_code >= 400:
        raise StripeGatewayError(f"Stripe checkout session creation failed: {response.text}")

    return response.json()


def _parse_signature_header(header_value: str) -> tuple[int, str]:
    timestamp = None
    signature = None

    for item in header_value.split(","):
        key, _, value = item.partition("=")
        if key == "t":
            timestamp = int(value)
        elif key == "v1":
            signature = value

    if timestamp is None or signature is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe-Signature header.",
        )
    return timestamp, signature


def verify_and_parse_webhook(raw_body: bytes, signature_header: str | None) -> dict[str, Any]:
    endpoint_secret = _require_webhook_secret()
    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe-Signature header.",
        )

    timestamp, expected_signature = _parse_signature_header(signature_header)
    if abs(int(time.time()) - timestamp) > 300:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe webhook timestamp is outside the allowed tolerance.",
        )

    signed_payload = f"{timestamp}.".encode("utf-8") + raw_body
    computed_signature = hmac.new(
        endpoint_secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(computed_signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe webhook signature verification failed.",
        )

    try:
        return json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe webhook payload is not valid JSON.",
        ) from exc
