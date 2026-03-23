from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.core.config import APP_ENV, APP_NAME, PUBLIC_BASE_URL, TARGET_SYSTEM
from app.routers.integrations import router as integrations_router
from app.routers.payments import router as payments_router

app = FastAPI(
    title=APP_NAME,
    version="0.3.0",
    description=(
        "A minimal FastAPI demo that showcases API request handling, Stripe test checkout, "
        "webhook verification, and payment status tracking."
    ),
)


@app.get("/", tags=["system"], response_class=HTMLResponse)
def home() -> str:
    return f"""
    <!doctype html>
    <html lang=\"en\">
      <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>{APP_NAME}</title>
        <style>
          body {{ font-family: Arial, sans-serif; max-width: 960px; margin: 40px auto; padding: 0 16px; line-height: 1.6; color: #1f2937; }}
          code, pre, input {{ font-family: Consolas, monospace; }}
          pre {{ background: #f5f5f5; padding: 12px; border-radius: 12px; overflow-x: auto; }}
          .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
          .card {{ border: 1px solid #e5e7eb; border-radius: 16px; padding: 18px; background: #fff; box-shadow: 0 4px 18px rgba(0,0,0,0.04); }}
          .muted {{ color: #6b7280; }}
          .row {{ display: grid; gap: 8px; margin-bottom: 12px; }}
          input {{ padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 10px; }}
          button {{ cursor: pointer; border: none; border-radius: 12px; padding: 12px 16px; font-weight: 600; }}
          .primary {{ background: #111827; color: #fff; }}
          .secondary {{ background: #f3f4f6; color: #111827; }}
          .result {{ white-space: pre-wrap; word-break: break-word; background: #f9fafb; padding: 12px; border-radius: 12px; min-height: 60px; }}
          a {{ color: #2563eb; text-decoration: none; }}
          ul {{ padding-left: 20px; }}
        </style>
      </head>
      <body>
        <h1>{APP_NAME}</h1>
        <p class=\"muted\">Environment: <strong>{APP_ENV}</strong> · Target system: <strong>{TARGET_SYSTEM}</strong></p>
        <p>This live demo shows a simple backend workflow: create a demo order, start a Stripe Checkout Session in test mode, then confirm the final status after Stripe sends webhook events.</p>

        <div class=\"grid\">
          <div class=\"card\">
            <h2>Test mode only</h2>
            <p>No real payment is processed.</p>
            <ul>
              <li>Card: <code>4242 4242 4242 4242</code></li>
              <li>Expiry: any future date</li>
              <li>CVC: any 3 digits</li>
              <li>Postal code: any value</li>
            </ul>
          </div>
          <div class=\"card\">
            <h2>Useful links</h2>
            <ul>
              <li><a href=\"/docs\">Swagger UI</a></li>
              <li><a href=\"/health\">Health check</a></li>
              <li><a href=\"{PUBLIC_BASE_URL}/openapi.json\">OpenAPI JSON</a></li>
            </ul>
          </div>
        </div>

        <div class=\"card\">
          <h2>Create demo order</h2>
          <div class=\"row\"><label>Order ID<input id=\"order_id\" value=\"DEMO-1001\" /></label></div>
          <div class=\"row\"><label>Name<input id=\"customer_name\" value=\"Alex Chen\" /></label></div>
          <div class=\"row\"><label>Email<input id=\"customer_email\" value=\"alex@example.com\" /></label></div>
          <div class=\"row\"><label>Amount (minor units)<input id=\"amount\" type=\"number\" value=\"499\" /></label></div>
          <div class=\"row\"><label>Currency<input id=\"currency\" value=\"usd\" /></label></div>
          <button class=\"primary\" onclick=\"createOrder()\">Create order</button>
          <p class=\"muted\">Example: <code>499</code> in <code>usd</code> means a $4.99 test payment.</p>
        </div>

        <div class=\"grid\">
          <div class=\"card\">
            <h2>Start Stripe Checkout</h2>
            <div class=\"row\"><label>Event ID<input id=\"event_id\" placeholder=\"evt_0001\" /></label></div>
            <button class=\"primary\" onclick=\"startCheckout()\">Create checkout session</button>
            <p class=\"muted\">This calls <code>POST /api/payments/checkout-session</code>.</p>
          </div>
          <div class=\"card\">
            <h2>Check status</h2>
            <div class=\"row\"><label>Event ID<input id=\"status_event_id\" placeholder=\"evt_0001\" /></label></div>
            <button class=\"secondary\" onclick=\"checkStatus()\">Get event status</button>
            <p class=\"muted\">This calls <code>GET /api/integrations/events/{{event_id}}</code>.</p>
          </div>
        </div>

        <div class=\"card\">
          <h2>Result</h2>
          <div id=\"result\" class=\"result\">Ready.</div>
        </div>

        <div class=\"card\">
          <h2>Demo flow</h2>
          <ol>
            <li>Create a demo order.</li>
            <li>Copy the returned <code>event_id</code>.</li>
            <li>Create a Stripe Checkout Session.</li>
            <li>Open the returned <code>checkout_url</code>.</li>
            <li>Pay with the test card on Stripe-hosted checkout.</li>
            <li>Wait a moment, then query the same <code>event_id</code> to confirm the updated status.</li>
          </ol>
        </div>

        <script>
          async function callApi(url, options) {{
            const response = await fetch(url, options);
            const data = await response.json();
            document.getElementById('result').textContent = JSON.stringify(data, null, 2);
            return data;
          }}

          async function createOrder() {{
            const payload = {{
              source: 'demo_store',
              order_id: document.getElementById('order_id').value,
              customer_name: document.getElementById('customer_name').value,
              customer_email: document.getElementById('customer_email').value,
              amount: Number(document.getElementById('amount').value),
              currency: document.getElementById('currency').value
            }};
            const data = await callApi('/api/integrations/orders', {{
              method: 'POST',
              headers: {{ 'Content-Type': 'application/json' }},
              body: JSON.stringify(payload)
            }});
            if (data.event_id) {{
              document.getElementById('event_id').value = data.event_id;
              document.getElementById('status_event_id').value = data.event_id;
            }}
          }}

          async function startCheckout() {{
            const eventId = document.getElementById('event_id').value;
            const data = await callApi('/api/payments/checkout-session', {{
              method: 'POST',
              headers: {{ 'Content-Type': 'application/json' }},
              body: JSON.stringify({{ event_id: eventId }})
            }});
            if (data.checkout_url) {{
              window.open(data.checkout_url, '_blank');
            }}
          }}

          async function checkStatus() {{
            const eventId = document.getElementById('status_event_id').value;
            await callApi(`/api/integrations/events/${{eventId}}`, {{ method: 'GET' }});
          }}
        </script>
      </body>
    </html>
    """


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/payments/success", tags=["payments"], response_class=HTMLResponse)
def payment_success(session_id: str | None = None) -> str:
    session_text = session_id or "(not provided)"
    return f"""
    <!doctype html>
    <html lang=\"en\"><body style=\"font-family: Arial, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px;\">
      <h1>Stripe test payment submitted</h1>
      <p>Your Checkout Session was completed in Stripe test mode.</p>
      <p>Session ID: <code>{session_text}</code></p>
      <p>Return to the home page and query the event status to confirm webhook processing.</p>
      <p><a href=\"/\">Back to demo home</a></p>
    </body></html>
    """


@app.get("/payments/cancel", tags=["payments"], response_class=HTMLResponse)
def payment_cancel(event_id: str | None = None) -> str:
    event_text = event_id or "(not provided)"
    return f"""
    <!doctype html>
    <html lang=\"en\"><body style=\"font-family: Arial, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px;\">
      <h1>Checkout cancelled</h1>
      <p>No payment was completed.</p>
      <p>Event ID: <code>{event_text}</code></p>
      <p><a href=\"/\">Back to demo home</a></p>
    </body></html>
    """


app.include_router(integrations_router)
app.include_router(payments_router)
