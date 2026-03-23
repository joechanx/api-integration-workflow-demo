from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.core.config import APP_ENV, APP_NAME, PUBLIC_BASE_URL, TARGET_SYSTEM
from app.routers.integrations import router as integrations_router
from app.routers.payments_ecpay import page_router as payment_pages_router
from app.routers.payments_ecpay import router as payments_router

app = FastAPI(
    title=APP_NAME,
    version="0.5.0",
    description="A minimal FastAPI demo that showcases API request handling, ECPay stage checkout, callback verification, browser return polling, and payment status tracking.",
)


@app.get("/", tags=["system"], response_class=HTMLResponse)
def home() -> str:
    return f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
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
        <p class="muted">Environment: <strong>{APP_ENV}</strong> · Target system: <strong>{TARGET_SYSTEM}</strong></p>
        <p>This live demo shows a practical payment flow: create a demo order, redirect to ECPay stage credit checkout, then let the result page auto-refresh until the server callback confirms the final status.</p>

        <div class="grid">
          <div class="card">
            <h2>ECPay stage only</h2>
            <p>No real payment is processed.</p>
            <ul>
              <li>Card: <code>4311-9522-2222-2222</code></li>
              <li>CVV: <code>222</code></li>
              <li>Expiry: any future date</li>
              <li>OTP: <code>1234</code> if prompted</li>
              <li>Currency: <code>TWD</code> only</li>
            </ul>
          </div>
          <div class="card">
            <h2>Useful links</h2>
            <ul>
              <li><a href="/docs">Swagger UI</a></li>
              <li><a href="/health">Health check</a></li>
              <li><a href="{PUBLIC_BASE_URL}/openapi.json">OpenAPI JSON</a></li>
            </ul>
          </div>
        </div>

        <div class="card">
          <h2>Create demo order</h2>
          <div class="row"><label>Order ID<input id="order_id" value="DEMO-1001" /></label></div>
          <div class="row"><label>Name<input id="customer_name" value="Alex Chen" /></label></div>
          <div class="row"><label>Email<input id="customer_email" value="alex@example.com" /></label></div>
          <div class="row"><label>Amount (TWD)<input id="amount" type="number" value="499" /></label></div>
          <div class="row"><label>Currency<input id="currency" value="TWD" /></label></div>
          <button class="primary" onclick="createOrder()">Create order</button>
          <p class="muted">Example: <code>499</code> in <code>TWD</code> means a NT$499 stage payment.</p>
        </div>

        <div class="grid">
          <div class="card">
            <h2>Open ECPay stage checkout</h2>
            <div class="row"><label>Event ID<input id="event_id" placeholder="evt_0001" /></label></div>
            <button class="primary" onclick="startCheckout()">Prepare checkout</button>
            <p class="muted">This calls <code>POST /api/payments/ecpay/checkout</code>.</p>
          </div>
          <div class="card">
            <h2>Check status</h2>
            <div class="row"><label>Event ID<input id="status_event_id" placeholder="evt_0001" /></label></div>
            <button class="secondary" onclick="checkStatus()">Get event status</button>
            <p class="muted">This calls <code>GET /api/integrations/events/{{event_id}}</code>.</p>
          </div>
        </div>

        <div class="card">
          <h2>Result</h2>
          <div id="result" class="result">Ready.</div>
        </div>

        <div class="card">
          <h2>Demo flow</h2>
          <ol>
            <li>Create a demo order.</li>
            <li>Copy the returned <code>event_id</code>.</li>
            <li>Prepare the ECPay stage credit checkout page.</li>
            <li>Complete the test payment on ECPay-hosted checkout.</li>
            <li>After the browser returns, the result page will auto-refresh until the callback confirms the final status.</li>
          </ol>
        </div>

        <script>
          async function callJsonApi(url, options) {{
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
            const data = await callJsonApi('/api/integrations/orders', {{
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
            const data = await callJsonApi('/api/payments/ecpay/checkout', {{
              method: 'POST',
              headers: {{ 'Content-Type': 'application/json' }},
              body: JSON.stringify({{ event_id: eventId }})
            }});
            if (data.payment_page_url) {{
              window.open(data.payment_page_url, '_blank');
            }}
          }}

          async function checkStatus() {{
            const eventId = document.getElementById('status_event_id').value;
            await callJsonApi(`/api/integrations/events/${{eventId}}`, {{ method: 'GET' }});
          }}
        </script>
      </body>
    </html>
    """


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(integrations_router)
app.include_router(payments_router)
app.include_router(payment_pages_router)
