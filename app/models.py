from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

EventStatus = Literal[
    "pending_payment",
    "redirect_ready",
    "payment_processing",
    "payment_callback_received",
    "paid",
    "payment_failed",
]


class OrderRequest(BaseModel):
    source: str = Field(..., min_length=2, max_length=50, examples=["demo_store"])
    order_id: str = Field(..., min_length=3, max_length=100, examples=["DEMO-1001"])
    customer_name: str = Field(..., min_length=2, max_length=100, examples=["Alex Chen"])
    customer_email: EmailStr = Field(..., examples=["alex@example.com"])
    amount: int = Field(..., gt=0, examples=[499])
    currency: str = Field(default="TWD", min_length=3, max_length=3, examples=["TWD"])

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        upper = value.upper()
        if upper != "TWD":
            raise ValueError("ECPay stage demo only supports TWD.")
        return upper


class MappedOrder(BaseModel):
    external_order_id: str
    client_name: str
    client_email: EmailStr
    total_amount: int
    currency: Literal["TWD"]
    source_platform: str


class EventRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    source: str
    status: EventStatus
    target_system: str
    mapped_payload: MappedOrder
    payment_page_url: str | None = None
    merchant_trade_no: str | None = None
    ecpay_trade_no: str | None = None
    payment_type: str | None = None
    rtn_code: int | None = None
    rtn_msg: str | None = None
    last_event_type: str | None = None
    message: str | None = None
    created_at: str
    updated_at: str


class CreateOrderResponse(BaseModel):
    event_id: str
    status: Literal["pending_payment"]
    target_system: str
    mapped_payload: MappedOrder
    next_step: str
    recent_lookup_url: str


class ECPayCheckoutRequest(BaseModel):
    event_id: str = Field(..., examples=["evt_8f0b2c9e2e4d4f7a8e3a9f53b2bf0eb4"])


class ECPayCheckoutResponse(BaseModel):
    event_id: str
    status: Literal["redirect_ready"]
    merchant_trade_no: str
    payment_page_url: str
    ecpay_checkout_url: str


class ECPayWebhookResponse(BaseModel):
    received: bool
    event_id: str | None = None
    merchant_trade_no: str | None = None
    status: EventStatus | None = None


class PublicCheckoutForm(BaseModel):
    source: str = "demo_store"
    order_id: str
    customer_name: str
    customer_email: EmailStr
    amount: int
    currency: str = "TWD"


class RecentEventsResponse(BaseModel):
    events: list[EventRecord]
