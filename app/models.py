from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

EventStatus = Literal[
    "pending_payment",
    "checkout_created",
    "payment_received",
    "paid",
    "payment_failed",
]


class OrderRequest(BaseModel):
    source: str = Field(..., min_length=2, max_length=50, examples=["demo_store"])
    order_id: str = Field(..., min_length=3, max_length=100, examples=["DEMO-1001"])
    customer_name: str = Field(..., min_length=2, max_length=100, examples=["Alex Chen"])
    customer_email: EmailStr = Field(..., examples=["alex@example.com"])
    amount: int = Field(..., gt=0, examples=[499])
    currency: str = Field(..., min_length=3, max_length=3, examples=["usd"])


class MappedOrder(BaseModel):
    external_order_id: str
    client_name: str
    client_email: EmailStr
    total_amount: int
    currency: str
    source_platform: str


class EventRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    source: str
    status: EventStatus
    target_system: str
    mapped_payload: MappedOrder
    checkout_url: str | None = None
    stripe_checkout_session_id: str | None = None
    stripe_payment_intent_id: str | None = None
    last_event_type: str | None = None
    message: str | None = None


class CreateOrderResponse(BaseModel):
    event_id: str
    status: Literal["pending_payment"]
    target_system: str
    mapped_payload: MappedOrder
    next_step: str


class CheckoutSessionRequest(BaseModel):
    event_id: str = Field(..., examples=["evt_0001"])


class CheckoutSessionResponse(BaseModel):
    event_id: str
    status: Literal["checkout_created"]
    checkout_session_id: str
    checkout_url: str


class StripeWebhookResponse(BaseModel):
    received: bool
    event_type: str
    event_id: str | None = None
    status: EventStatus | None = None


class PublicCheckoutForm(BaseModel):
    source: str = "demo_store"
    order_id: str
    customer_name: str
    customer_email: EmailStr
    amount: int
    currency: str = "usd"
