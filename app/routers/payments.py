from fastapi import APIRouter

from app.models import CheckoutSessionRequest, CheckoutSessionResponse
from app.services.processor import start_checkout_for_event

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.post("/checkout-session", response_model=CheckoutSessionResponse)
def create_checkout_session_for_event(payload: CheckoutSessionRequest) -> CheckoutSessionResponse:
    return start_checkout_for_event(payload.event_id)
