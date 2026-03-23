from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.models import ECPayCheckoutRequest, ECPayCheckoutResponse
from app.services.ecpay_service import checkout_action_url
from app.services.processor import build_redirect_context, mark_browser_return, prepare_ecpay_checkout

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
async def ecpay_result_page(request: Request) -> str:
    form_data: dict[str, str] = {}
    if request.method == "POST":
        form = await request.form()
        form_data = {key: str(value) for key, value in form.items()}

    event = mark_browser_return(form_data) if form_data else None
    event_id = request.query_params.get("event_id") or (event.event_id if event else form_data.get("CustomField1")) or ""
    merchant_trade_no = form_data.get("MerchantTradeNo") or (event.merchant_trade_no if event else "")
    return _build_result_page(event_id=event_id, merchant_trade_no=merchant_trade_no)


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


def _build_result_page(event_id: str, merchant_trade_no: str) -> str:
    safe_event_id = _escape_html(event_id)
    safe_trade_no = _escape_html(merchant_trade_no)
    polling_block = ""
    if event_id:
        polling_block = f"""
        <script>
          const eventId = "{safe_event_id}";
          const statusUrl = `/api/integrations/events/${{eventId}}`;
          const statusEl = document.getElementById('status-box');
          const summaryEl = document.getElementById('summary');
          const countdownEl = document.getElementById('countdown');
          let attempts = 0;
          const maxAttempts = 15;

          function renderState(data) {{
            statusEl.textContent = JSON.stringify(data, null, 2);
            if (data.status === 'paid') {{
              summaryEl.textContent = 'Payment confirmed. The ECPay server callback has updated the demo event.';
              summaryEl.style.color = '#166534';
              return true;
            }}
            if (data.status === 'payment_failed') {{
              summaryEl.textContent = 'Payment failed or was declined. Review the returned event data below.';
              summaryEl.style.color = '#991b1b';
              return true;
            }}
            if (data.status === 'payment_processing' || data.status === 'redirect_ready') {{
              summaryEl.textContent = 'Payment was submitted. Waiting for the ECPay server callback to confirm the final result.';
              summaryEl.style.color = '#92400e';
            }} else {{
              summaryEl.textContent = 'Waiting for the latest event status.';
              summaryEl.style.color = '#374151';
            }}
            return false;
          }}

          async function pollStatus() {{
            attempts += 1;
            countdownEl.textContent = `Auto-refresh ${{attempts}}/${{maxAttempts}}`;

            try {{
              const response = await fetch(statusUrl);
              const data = await response.json();
              const done = renderState(data);
              if (!done && attempts < maxAttempts) {{
                setTimeout(pollStatus, 2000);
              }} else if (!done) {{
                summaryEl.textContent = 'Still syncing. Use the refresh button below to check again.';
                summaryEl.style.color = '#374151';
              }}
            }} catch (error) {{
              statusEl.textContent = `Unable to load event status: ${{error}}`;
              summaryEl.textContent = 'Status check failed. Use the refresh button below to try again.';
              summaryEl.style.color = '#991b1b';
            }}
          }}

          async function refreshNow() {{
            attempts = 0;
            await pollStatus();
          }}

          window.refreshNow = refreshNow;
          pollStatus();
        </script>
        """
    return f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>ECPay payment status</title>
      </head>
      <body style="font-family: Arial, sans-serif; max-width: 820px; margin: 40px auto; padding: 0 16px; line-height: 1.6; color: #1f2937;">
        <h1>Payment submitted. Final status is syncing.</h1>
        <p>The browser returned from ECPay, but the live demo confirms success only after the server callback arrives.</p>
        <p id="summary" style="font-weight: 700;">Checking latest event status...</p>
        <div style="display: grid; gap: 8px; margin: 20px 0;">
          <div>Event ID: <code>{safe_event_id or '(not detected)'}</code></div>
          <div>MerchantTradeNo: <code>{safe_trade_no or '(not detected)'}</code></div>
          <div id="countdown" style="color: #6b7280;">Auto-refresh pending</div>
        </div>
        <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px;">
          <button onclick="refreshNow()" style="cursor: pointer; border: none; border-radius: 12px; padding: 12px 16px; font-weight: 600; background: #111827; color: #fff;">Refresh payment status</button>
          <a href="/" style="display: inline-block; text-decoration: none; border-radius: 12px; padding: 12px 16px; background: #f3f4f6; color: #111827; font-weight: 600;">Back to demo home</a>
          <a href="/docs" style="display: inline-block; text-decoration: none; border-radius: 12px; padding: 12px 16px; background: #f3f4f6; color: #111827; font-weight: 600;">Open Swagger UI</a>
        </div>
        <pre id="status-box" style="white-space: pre-wrap; word-break: break-word; background: #f9fafb; padding: 14px; border-radius: 14px; min-height: 180px;">Waiting for event status...</pre>
        <p style="color: #6b7280;">For ECPay demo flows, the client redirect can arrive before the server callback. This page keeps checking until the final result is confirmed.</p>
        {polling_block}
      </body>
    </html>
    """


def _escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
