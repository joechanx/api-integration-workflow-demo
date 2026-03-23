from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, status

from app.core.config import TARGET_SYSTEM
from app.models import (
    CreateOrderResponse,
    ECPayCheckoutResponse,
    ECPayWebhookResponse,
    EventRecord,
    OrderRequest,
)
from app.services.ecpay_service import build_checkout_payload, checkout_action_url
from app.services.mapper import map_order_payload
from app.services.store import event_store


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_integration_event(order: OrderRequest) -> CreateOrderResponse:
    mapped_payload = map_order_payload(order)
    event_id = f"evt_{uuid4().hex}"
    now = _utc_now_iso()

    event = EventRecord(
        event_id=event_id,
        source=order.source,
        status="pending_payment",
        target_system=TARGET_SYSTEM,
        mapped_payload=mapped_payload,
        message="Order created. Ready to open ECPay stage credit checkout.",
        created_at=now,
        updated_at=now,
    )
    event_store.save(event)

    return CreateOrderResponse(
        event_id=event_id,
        status="pending_payment",
        target_system=TARGET_SYSTEM,
        mapped_payload=mapped_payload,
        next_step="POST /api/payments/ecpay/checkout",
        recent_lookup_url=f"/api/integrations/events/{event_id}",
    )


def prepare_ecpay_checkout(event_id: str) -> ECPayCheckoutResponse:
    existing_event = event_store.get(event_id)
    if existing_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event '{event_id}' not found.",
        )

    payload = build_checkout_payload(existing_event)
    payment_page_url = f"/payments/ecpay/redirect/{event_id}"
    updated_event = existing_event.model_copy(
        update={
            "status": "redirect_ready",
            "payment_page_url": payment_page_url,
            "merchant_trade_no": payload["MerchantTradeNo"],
            "last_event_type": "ecpay.checkout.form_created",
            "message": "ECPay stage checkout form is ready.",
        }
    )
    event_store.update(event_id, updated_event)

    return ECPayCheckoutResponse(
        event_id=event_id,
        status="redirect_ready",
        merchant_trade_no=payload["MerchantTradeNo"],
        payment_page_url=payment_page_url,
        ecpay_checkout_url=checkout_action_url(),
    )


def build_redirect_context(event_id: str) -> tuple[EventRecord, dict[str, str]]:
    event = get_event_status(event_id)
    payload = build_checkout_payload(event)
    if event.merchant_trade_no != payload["MerchantTradeNo"]:
        event = event.model_copy(update={"merchant_trade_no": payload["MerchantTradeNo"]})
        event_store.update(event_id, event)
    return event, payload


def mark_browser_return(form_data: dict[str, str]) -> EventRecord | None:
    event = _resolve_event(form_data)
    if event is None:
        return None

    if event.status in {"paid", "payment_failed"}:
        return event

    rtn_msg = form_data.get("RtnMsg") or event.rtn_msg
    updated_event = event.model_copy(
        update={
            "status": "payment_processing",
            "merchant_trade_no": form_data.get("MerchantTradeNo") or event.merchant_trade_no,
            "rtn_msg": rtn_msg,
            "last_event_type": "ecpay.order_result_url",
            "message": "Browser returned from ECPay. Waiting for server callback confirmation.",
        }
    )
    event_store.update(event.event_id, updated_event)
    return updated_event


def handle_ecpay_return(form_data: dict[str, str]) -> ECPayWebhookResponse:
    event = _resolve_event(form_data)
    merchant_trade_no = form_data.get("MerchantTradeNo")
    rtn_code_value = form_data.get("RtnCode")
    rtn_msg = form_data.get("RtnMsg")
    payment_type = form_data.get("PaymentType")

    if event is None:
        return ECPayWebhookResponse(received=True, merchant_trade_no=merchant_trade_no)

    rtn_code = _safe_int(rtn_code_value)
    status_value = "paid" if rtn_code == 1 else "payment_failed"
    message = (
        "ECPay callback verified and payment succeeded."
        if rtn_code == 1
        else "ECPay callback verified but payment failed."
    )

    updated_event = event.model_copy(
        update={
            "status": status_value,
            "merchant_trade_no": merchant_trade_no or event.merchant_trade_no,
            "ecpay_trade_no": form_data.get("TradeNo") or event.ecpay_trade_no,
            "payment_type": payment_type or event.payment_type,
            "rtn_code": rtn_code,
            "rtn_msg": rtn_msg or event.rtn_msg,
            "last_event_type": "ecpay.return_url",
            "message": message,
        }
    )
    event_store.update(event.event_id, updated_event)

    return ECPayWebhookResponse(
        received=True,
        event_id=event.event_id,
        merchant_trade_no=merchant_trade_no,
        status=updated_event.status,
    )


def get_event_status(event_id: str) -> EventRecord:
    event = event_store.get(event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event '{event_id}' not found.",
        )
    return event


def list_recent_events(limit: int = 5) -> list[EventRecord]:
    return event_store.list_recent(limit=limit)


def _resolve_event(form_data: dict[str, str]) -> EventRecord | None:
    event_id = form_data.get("CustomField1")
    if event_id:
        event = event_store.get(event_id)
        if event is not None:
            return event

    merchant_trade_no = form_data.get("MerchantTradeNo")
    if merchant_trade_no:
        return event_store.get_by_merchant_trade_no(merchant_trade_no)
    return None


def _safe_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None
