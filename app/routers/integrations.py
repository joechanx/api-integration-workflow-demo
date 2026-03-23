from fastapi import APIRouter, Header, Request

from app.models import CreateOrderResponse, EventRecord, OrderRequest, StripeWebhookResponse
from app.services.processor import create_integration_event, get_event_status, handle_stripe_event
from app.services.stripe_gateway import verify_and_parse_webhook

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.post("/orders", response_model=CreateOrderResponse)
def create_order_integration(order: OrderRequest) -> CreateOrderResponse:
    return create_integration_event(order)


@router.post("/webhooks/stripe", response_model=StripeWebhookResponse)
async def stripe_webhook_callback(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
) -> StripeWebhookResponse:
    raw_body = await request.body()
    event_payload = verify_and_parse_webhook(raw_body, stripe_signature)
    return handle_stripe_event(event_payload)


@router.get("/events/{event_id}", response_model=EventRecord)
def get_integration_event(event_id: str) -> EventRecord:
    return get_event_status(event_id)
