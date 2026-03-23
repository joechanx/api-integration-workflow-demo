from typing import Any

from fastapi import HTTPException, status

from app.core.config import TARGET_SYSTEM
from app.models import (
    CheckoutSessionResponse,
    CreateOrderResponse,
    EventRecord,
    OrderRequest,
    StripeWebhookResponse,
)
from app.services.mapper import map_order_payload
from app.services.store import event_store
from app.services.stripe_gateway import StripeGatewayError, create_checkout_session


def create_integration_event(order: OrderRequest) -> CreateOrderResponse:
    mapped_payload = map_order_payload(order)
    event_id = event_store.next_event_id()

    event = EventRecord(
        event_id=event_id,
        source=order.source,
        status="pending_payment",
        target_system=TARGET_SYSTEM,
        mapped_payload=mapped_payload,
        message="Order created. Ready to open Stripe Checkout in test mode.",
    )
    event_store.save(event)

    return CreateOrderResponse(
        event_id=event_id,
        status="pending_payment",
        target_system=TARGET_SYSTEM,
        mapped_payload=mapped_payload,
        next_step="POST /api/payments/checkout-session",
    )


def start_checkout_for_event(event_id: str) -> CheckoutSessionResponse:
    existing_event = event_store.get(event_id)
    if existing_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event '{event_id}' not found.",
        )

    try:
        session = create_checkout_session(existing_event)
    except StripeGatewayError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    updated_event = existing_event.model_copy(
        update={
            "status": "checkout_created",
            "checkout_url": session["url"],
            "stripe_checkout_session_id": session["id"],
            "last_event_type": "checkout.session.created",
            "message": "Stripe Checkout Session created in test mode.",
        }
    )
    event_store.update(event_id, updated_event)

    return CheckoutSessionResponse(
        event_id=event_id,
        status="checkout_created",
        checkout_session_id=session["id"],
        checkout_url=session["url"],
    )


def handle_stripe_event(event_payload: dict[str, Any]) -> StripeWebhookResponse:
    event_type = event_payload.get("type", "unknown")
    data_object = event_payload.get("data", {}).get("object", {})

    event_id = _extract_internal_event_id(event_type, data_object)
    if event_id is None:
        return StripeWebhookResponse(received=True, event_type=event_type)

    existing_event = event_store.get(event_id)
    if existing_event is None:
        return StripeWebhookResponse(received=True, event_type=event_type, event_id=event_id)

    status_value, message = _map_event_type_to_status(event_type)
    updated_event = existing_event.model_copy(
        update={
            "status": status_value,
            "stripe_checkout_session_id": data_object.get("id")
            if event_type == "checkout.session.completed"
            else existing_event.stripe_checkout_session_id,
            "stripe_payment_intent_id": data_object.get("payment_intent")
            if event_type == "checkout.session.completed"
            else data_object.get("id", existing_event.stripe_payment_intent_id),
            "last_event_type": event_type,
            "message": message,
        }
    )
    event_store.update(event_id, updated_event)

    return StripeWebhookResponse(
        received=True,
        event_type=event_type,
        event_id=event_id,
        status=updated_event.status,
    )


def _extract_internal_event_id(event_type: str, data_object: dict[str, Any]) -> str | None:
    if event_type == "checkout.session.completed":
        return data_object.get("client_reference_id") or data_object.get("metadata", {}).get("event_id")

    if event_type.startswith("payment_intent."):
        return data_object.get("metadata", {}).get("event_id")

    return data_object.get("metadata", {}).get("event_id")


def _map_event_type_to_status(event_type: str) -> tuple[str, str]:
    if event_type == "checkout.session.completed":
        return "payment_received", "Stripe Checkout completed in test mode."
    if event_type == "payment_intent.succeeded":
        return "paid", "Stripe payment intent succeeded in test mode."
    if event_type == "payment_intent.payment_failed":
        return "payment_failed", "Stripe payment intent failed in test mode."
    return "payment_received", f"Received Stripe event: {event_type}."


def get_event_status(event_id: str) -> EventRecord:
    event = event_store.get(event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event '{event_id}' not found.",
        )
    return event
