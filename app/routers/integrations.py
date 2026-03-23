from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from app.models import CreateOrderResponse, ECPayWebhookResponse, EventRecord, OrderRequest
from app.services.ecpay_checkmac import verify_check_mac_value
from app.services.processor import create_integration_event, get_event_status, handle_ecpay_return

router = APIRouter(prefix="/api/integrations", tags=["integrations"])


@router.post("/orders", response_model=CreateOrderResponse)
def create_order_integration(order: OrderRequest) -> CreateOrderResponse:
    return create_integration_event(order)


@router.post("/webhooks/ecpay/return", response_class=PlainTextResponse)
async def ecpay_return_callback(request: Request) -> PlainTextResponse:
    form = await request.form()
    form_data = {key: str(value) for key, value in form.items()}
    if not verify_check_mac_value(form_data):
        return PlainTextResponse("0|CheckMacValue Error", status_code=400)

    handle_ecpay_return(form_data)
    return PlainTextResponse("1|OK")


@router.get("/events/{event_id}", response_model=EventRecord)
def get_integration_event(event_id: str) -> EventRecord:
    return get_event_status(event_id)
