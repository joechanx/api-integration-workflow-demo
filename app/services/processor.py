from fastapi import HTTPException, status

from app.core.config import TARGET_SYSTEM
from app.models import (
    CreateOrderResponse,
    EventRecord,
    OrderRequest,
    WebhookCallbackRequest,
    WebhookCallbackResponse,
)
from app.services.mapper import map_order_payload
from app.services.store import event_store


def create_integration_event(order: OrderRequest) -> CreateOrderResponse:
    mapped_payload = map_order_payload(order)
    event_id = event_store.next_event_id()

    event = EventRecord(
        event_id=event_id,
        source=order.source,
        status="received",
        target_system=TARGET_SYSTEM,
        mapped_payload=mapped_payload,
    )
    event_store.save(event)

    return CreateOrderResponse(
        event_id=event_id,
        status="received",
        target_system=TARGET_SYSTEM,
        mapped_payload=mapped_payload,
        webhook_hint="POST /api/integrations/webhooks/erp",
    )


def apply_erp_webhook(callback: WebhookCallbackRequest) -> WebhookCallbackResponse:
    existing_event = event_store.get(callback.event_id)
    if existing_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event '{callback.event_id}' not found.",
        )

    updated_event = existing_event.model_copy(
        update={
            "status": callback.result,
            "external_reference": callback.reference_id,
            "message": callback.message,
        }
    )
    event_store.update(callback.event_id, updated_event)

    return WebhookCallbackResponse(
        event_id=updated_event.event_id,
        status=updated_event.status,
        reference_id=updated_event.external_reference,
        message=updated_event.message,
    )


def get_event_status(event_id: str) -> EventRecord:
    event = event_store.get(event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event '{event_id}' not found.",
        )
    return event
