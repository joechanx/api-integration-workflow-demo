from datetime import datetime
from secrets import token_hex

from fastapi import HTTPException, status

from app.core.config import ECPAY_CHECKOUT_URL, ECPAY_MERCHANT_ID, PUBLIC_BASE_URL
from app.models import EventRecord
from app.services.ecpay_checkmac import generate_check_mac_value


def build_checkout_payload(event: EventRecord) -> dict[str, str]:
    if event.mapped_payload.currency != "TWD":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ECPay stage demo only supports TWD.",
        )

    merchant_trade_no = event.merchant_trade_no or _generate_merchant_trade_no()
    payload = {
        "MerchantID": ECPAY_MERCHANT_ID,
        "MerchantTradeNo": merchant_trade_no,
        "MerchantTradeDate": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": str(event.mapped_payload.total_amount),
        "TradeDesc": "API integration workflow demo",
        "ItemName": f"Demo Order {event.mapped_payload.external_order_id}",
        "ReturnURL": f"{PUBLIC_BASE_URL}/api/integrations/webhooks/ecpay/return",
        "OrderResultURL": f"{PUBLIC_BASE_URL}/payments/ecpay/result",
        "ClientBackURL": f"{PUBLIC_BASE_URL}/payments/ecpay/back?event_id={event.event_id}",
        "ChoosePayment": "Credit",
        "NeedExtraPaidInfo": "Y",
        "EncryptType": "1",
        "CustomField1": event.event_id,
        "CustomField2": event.mapped_payload.external_order_id,
        "CustomField3": event.mapped_payload.client_email,
        "CustomField4": event.source,
    }
    payload["CheckMacValue"] = generate_check_mac_value(payload)
    return payload


def checkout_action_url() -> str:
    return ECPAY_CHECKOUT_URL


def _generate_merchant_trade_no() -> str:
    timestamp = datetime.now().strftime("%y%m%d%H%M%S")
    suffix = token_hex(3).upper()
    return f"DM{timestamp}{suffix}"
