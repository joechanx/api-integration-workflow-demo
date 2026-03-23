from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.models import ECPayCheckoutRequest, ECPayCheckoutResponse
from app.services.ecpay_service import checkout_action_url
from app.services.processor import build_redirect_context, prepare_ecpay_checkout

router = APIRouter(prefix="/api/payments/ecpay", tags=["payments"])
page_router = APIRouter(tags=["payment-pages"])


@router.post("/checkout", response_model=ECPayCheckoutResponse)
def create_ecpay_checkout_for_event(payload: ECPayCheckoutRequest) -> ECPayCheckoutResponse:
    return prepare_ecpay_checkout(payload.event_id)


@page_router.get("/payments/ecpay/redirect/{event_id}", response_class=HTMLResponse)
def ecpay_redirect_page(event_id: str) -> str:
    event, payload = build_redirect_context(event_id)
    action_url = checkout_action_url()
    inputs = "\n".join(
        f'<input type="hidden" name="{key}" value="{_escape_html(value)}" />'
        for key, value in payload.items()
    )
    return f"""
    <!doctype html>
    <html lang="en"><body style="font-family: Arial, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px;">
      <h1>Redirecting to ECPay stage checkout</h1>
      <p>Event ID: <code>{event.event_id}</code></p>
      <p>MerchantTradeNo: <code>{event.merchant_trade_no or payload['MerchantTradeNo']}</code></p>
      <p>If the redirect does not start automatically, click the button below.</p>
      <form id="ecpay-form" method="post" action="{_escape_html(action_url)}">
        {inputs}
        <button type="submit">Continue to ECPay stage checkout</button>
      </form>
      <script>document.getElementById('ecpay-form').submit();</script>
    </body></html>
    """


@page_router.api_route("/payments/ecpay/result", methods=["GET", "POST"], response_class=HTMLResponse)
def ecpay_result_page(request: Request) -> str:
    return """
    <!doctype html>
    <html lang="en"><body style="font-family: Arial, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px;">
      <h1>ECPay checkout result received</h1>
      <p>The browser was redirected back from ECPay. The final payment state should still be confirmed by the server callback.</p>
      <p>Return to the demo home page and query the event status.</p>
      <p><a href="/">Back to demo home</a></p>
    </body></html>
    """


@page_router.get("/payments/ecpay/back", response_class=HTMLResponse)
def ecpay_back_page(event_id: str | None = None) -> str:
    event_text = event_id or "(not provided)"
    return f"""
    <!doctype html>
    <html lang="en"><body style="font-family: Arial, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px;">
      <h1>Returned to demo site</h1>
      <p>No final payment status is derived from this page alone.</p>
      <p>Event ID: <code>{_escape_html(event_text)}</code></p>
      <p><a href="/">Back to demo home</a></p>
    </body></html>
    """


def _escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
