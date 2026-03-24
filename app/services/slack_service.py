from __future__ import annotations

from typing import Literal

import httpx

from app.core.config import (
    PUBLIC_BASE_URL,
    SLACK_CHANNEL_LABEL,
    SLACK_NOTIFICATIONS_ENABLED,
    SLACK_WEBHOOK_URL,
)
from app.models import EventRecord

NotificationResult = tuple[Literal["sent", "disabled", "failed", "not_applicable"], str | None]


def send_payment_notification(event: EventRecord) -> NotificationResult:
    if event.status != "paid":
        return ("not_applicable", None)
    if not SLACK_NOTIFICATIONS_ENABLED or not SLACK_WEBHOOK_URL:
        return ("disabled", None)

    payload = {
        "text": f"Payment confirmed for {event.mapped_payload.external_order_id} ({event.event_id})",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "Payment confirmed in demo"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Event ID*\n`{event.event_id}`"},
                    {"type": "mrkdwn", "text": f"*Order ID*\n`{event.mapped_payload.external_order_id}`"},
                    {"type": "mrkdwn", "text": f"*Amount*\n{event.mapped_payload.total_amount} {event.mapped_payload.currency}"},
                    {"type": "mrkdwn", "text": f"*MerchantTradeNo*\n`{event.merchant_trade_no or '-'} `"},
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Final status: *{event.status}*\nView live demo event: <{PUBLIC_BASE_URL}/payments/ecpay/result?event_id={event.event_id}|open status page>",
                },
            },
        ],
    }

    try:
        response = httpx.post(SLACK_WEBHOOK_URL, json=payload, timeout=10.0)
        if response.status_code == 200 and response.text.strip().lower() == "ok":
            return ("sent", None)
        return ("failed", f"Slack webhook returned {response.status_code}: {response.text[:200]}")
    except Exception as exc:  # pragma: no cover
        return ("failed", str(exc))


def notification_channel_label() -> str:
    return SLACK_CHANNEL_LABEL
