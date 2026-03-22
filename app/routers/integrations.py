from fastapi import APIRouter

from app.models import (
    CreateOrderResponse,
    EventRecord,
    OrderRequest,
    WebhookCallbackRequest,
    WebhookCallbackResponse,
)
from app.services.processor import apply_erp_webhook, create_integration_event, get_event_status

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.post("/orders", response_model=CreateOrderResponse)
def create_order_integration(order: OrderRequest) -> CreateOrderResponse:
    return create_integration_event(order)


@router.post("/webhooks/erp", response_model=WebhookCallbackResponse)
def erp_webhook_callback(callback: WebhookCallbackRequest) -> WebhookCallbackResponse:
    return apply_erp_webhook(callback)


@router.get("/events/{event_id}", response_model=EventRecord)
def get_integration_event(event_id: str) -> EventRecord:
    return get_event_status(event_id)
