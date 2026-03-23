from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.core.config import APP_ENV, APP_NAME, APP_DB_PATH, PUBLIC_BASE_URL, TARGET_SYSTEM
from app.routers.integrations import router as integrations_router
from app.routers.payments_ecpay import page_router as payment_pages_router
from app.routers.payments_ecpay import router as payments_router

app = FastAPI(
    title=APP_NAME,
    version="0.6.0",
    description="A minimal FastAPI demo that showcases API request handling, ECPay stage checkout, callback verification, persistent SQLite event tracking, and reload-safe payment status pages.",
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
          body {{ font-family: Arial, sans-serif; max-width: 1080px; margin: 40px auto; padding: 0 16px; line-height: 1.6; color: #1f2937; }}
          code, pre, input, textarea {{ font-family: Consolas, monospace; }}
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
          table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
          th, td {{ border-bottom: 1px solid #e5e7eb; text-align: left; padding: 8px 6px; vertical-align: top; }}
          .small {{ font-size: 13px; }}
        </style>
      </head>
      <body>
        <h1>{APP_NAME}</h1>
        <p class="muted">Environment: <strong>{APP_ENV}</strong> · Target system: <strong>{TARGET_SYSTEM}</strong> · Storage: <code>{APP_DB_PATH}</code></p>
        <p>This live demo shows a practical payment flow: create a demo order, redirect to ECPay stage credit checkout, then let the result page auto-refresh until the server callback confirms the final status. Orders are stored in SQLite so Railway restarts do not reset the demo history.</p>

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
          <div class="row"><label>Order ID<input id="order_id" /></label></div>
          <div class="row"><label>Name<input id="customer_name" value="Alex Chen" /></label></div>
          <div class="row"><label>Email<input id="customer_email" value="alex@example.com" /></label></div>
          <div class="row"><label>Amount (TWD)<input id="amount" type="number" value="499" /></label></div>
          <div class="row"><label>Currency<input id="currency" value="TWD" /></label></div>
          <button class="primary" onclick="createOrder()">Create order</button>
          <p class="muted">A new order is only created when you click the button. Reloading this page does not create another payment event.</p>
        </div>

        <div class="grid">
          <div class="card">
            <h2>Open ECPay stage checkout</h2>
            <div class="row"><label>Event ID<input id="event_id" placeholder="evt_xxx" /></label></div>
            <button class="primary" onclick="startCheckout()">Prepare checkout</button>
            <p class="muted">This calls <code>POST /api/payments/ecpay/checkout</code>.</p>
          </div>
          <div class="card">
            <h2>Check status</h2>
            <div class="row"><label>Event ID<input id="status_event_id" placeholder="evt_xxx" /></label></div>
            <button class="secondary" onclick="checkStatus()">Get event status</button>
            <p class="muted">This calls <code>GET /api/integrations/events/{{event_id}}</code>.</p>
          </div>
        </div>

        <div class="card">
          <h2>Result</h2>
          <div id="result" class="result">Ready.</div>
        </div>

        <div class="card">
          <h2>Recent events</h2>
          <p class="muted small">These are stored in SQLite so callback updates can still be found after page reloads or service restarts.</p>
          <button class="secondary" onclick="loadRecentEvents()">Refresh recent events</button>
          <div id="recent-events" class="result" style="margin-top:12px;">Loading…</div>
        </div>

        <div class="card">
          <h2>Demo flow</h2>
          <ol>
            <li>Create a demo order.</li>
            <li>Copy the returned <code>event_id</code>.</li>
            <li>Prepare the ECPay stage credit checkout page.</li>
            <li>Complete the test payment on ECPay-hosted checkout.</li>
            <li>The result page keeps the <code>event_id</code> in its URL, so reload continues checking the same payment.</li>
          </ol>
        </div>

        <script>
          function generateOrderId() {{
            const now = new Date();
            const pad = (n) => String(n).padStart(2, '0');
            return `DEMO-${{now.getFullYear()}}${{pad(now.getMonth()+1)}}${{pad(now.getDate())}}-${{pad(now.getHours())}}${{pad(now.getMinutes())}}${{pad(now.getSeconds())}}`;
          }}

          function setLatestEventId(eventId) {{
            if (!eventId) return;
            localStorage.setItem('latest_event_id', eventId);
            document.getElementById('event_id').value = eventId;
            document.getElementById('status_event_id').value = eventId;
          }}

          function renderRecentEvents(events) {{
            const container = document.getElementById('recent-events');
            if (!events.length) {{
              container.textContent = 'No events yet.';
              return;
            }}
            const rows = events.map((event) => `
              <tr>
                <td><code>${{event.event_id}}</code></td>
                <td>${{event.status}}</td>
                <td><code>${{event.merchant_trade_no || ''}}</code></td>
                <td>${{event.mapped_payload.external_order_id}}</td>
                <td>${{new Date(event.updated_at).toLocaleString()}}</td>
                <td><button class="secondary" onclick="reuseEvent('${{event.event_id}}')">Use</button></td>
              </tr>
            `).join('');
            container.innerHTML = `<table><thead><tr><th>Event ID</th><th>Status</th><th>MerchantTradeNo</th><th>Order ID</th><th>Updated</th><th></th></tr></thead><tbody>${{rows}}</tbody></table>`;
          }}

          async function loadRecentEvents() {{
            const response = await fetch('/api/integrations/events?limit=8');
            const data = await response.json();
            renderRecentEvents(data.events || []);
            if (data.events && data.events.length && !document.getElementById('event_id').value) {{
              setLatestEventId(data.events[0].event_id);
            }}
          }}

          function reuseEvent(eventId) {{
            setLatestEventId(eventId);
          }}

          async function callJsonApi(url, options) {{
            const response = await fetch(url, options);
            const data = await response.json();
            document.getElementById('result').textContent = JSON.stringify(data, null, 2);
            return data;
          }}

          async function createOrder() {{
            const payload = {{
              source: 'demo_store',
              order_id: document.getElementById('order_id').value || generateOrderId(),
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
              setLatestEventId(data.event_id);
              document.getElementById('order_id').value = generateOrderId();
              loadRecentEvents();
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
              window.location.href = data.payment_page_url;
            }}
          }}

          async function checkStatus() {{
            const eventId = document.getElementById('status_event_id').value;
            await callJsonApi(`/api/integrations/events/${{eventId}}`, {{ method: 'GET' }});
          }}

          document.getElementById('order_id').value = generateOrderId();
          const latestEventId = localStorage.getItem('latest_event_id');
          if (latestEventId) setLatestEventId(latestEventId);
          loadRecentEvents();
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
