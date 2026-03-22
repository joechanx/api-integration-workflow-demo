from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrderRequest(BaseModel):
    source: str = Field(..., min_length=2, max_length=50, examples=["shopify"])
    order_id: str = Field(..., min_length=3, max_length=100, examples=["SHP-1001"])
    customer_name: str = Field(..., min_length=2, max_length=100, examples=["Alex Chen"])
    customer_email: EmailStr = Field(..., examples=["alex@example.com"])
    amount: int = Field(..., gt=0, examples=[1299])
    currency: str = Field(..., min_length=3, max_length=3, examples=["TWD"])


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
    status: Literal["received", "processed", "failed"]
    target_system: str
    mapped_payload: MappedOrder
    external_reference: str | None = None
    message: str | None = None


class CreateOrderResponse(BaseModel):
    event_id: str
    status: Literal["received"]
    target_system: str
    mapped_payload: MappedOrder
    webhook_hint: str


class WebhookCallbackRequest(BaseModel):
    event_id: str = Field(..., examples=["evt_0001"])
    result: Literal["processed", "failed"]
    reference_id: str | None = Field(default=None, examples=["ERP-2026-0001"])
    message: str | None = Field(default=None, max_length=250, examples=["Order synced successfully"])


class WebhookCallbackResponse(BaseModel):
    event_id: str
    status: Literal["processed", "failed"]
    reference_id: str | None = None
    message: str | None = None
