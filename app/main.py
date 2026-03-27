
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.core.config import APP_ENV, APP_NAME, APP_DB_PATH, PUBLIC_BASE_URL, SLACK_CHANNEL_LABEL, SLACK_NOTIFICATIONS_ENABLED, TARGET_SYSTEM
from app.routers.integrations import router as integrations_router
from app.routers.payments_ecpay import page_router as payment_pages_router
from app.routers.payments_ecpay import router as payments_router

app = FastAPI(
    title=APP_NAME,
    version="0.7.0",
    description="A minimal FastAPI demo that showcases API request handling, ECPay stage checkout, callback verification, persistent SQLite event tracking, reload-safe payment status pages, and optional Slack notification delivery after confirmed payment.",
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
          :root {{
            --bg: #f1f5f9;
            --panel: #ffffff;
            --panel-soft: #f8fafc;
            --text: #0f172a;
            --muted: #64748b;
            --line: #e2e8f0;
            --primary: #111827;
            --accent: #4f46e5;
            --accent-soft: #eef2ff;
            --success: #059669;
            --success-soft: #ecfdf5;
            --warning: #d97706;
            --warning-soft: #fffbeb;
            --danger: #dc2626;
            --danger-soft: #fef2f2;
            --shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
            --radius-xl: 28px;
            --radius-lg: 20px;
            --radius-md: 14px;
          }}

          * {{ box-sizing: border-box; }}
          body {{
            margin: 0;
            background: var(--bg);
            color: var(--text);
            font-family: Inter, Arial, sans-serif;
            line-height: 1.6;
          }}

          code, pre, input, textarea, button {{
            font-family: Inter, Consolas, monospace;
          }}

          a {{
            color: #2563eb;
            text-decoration: none;
          }}

          .wrap {{
            max-width: 1180px;
            margin: 0 auto;
            padding: 28px 18px 42px;
          }}

          .hero {{
            display: grid;
            grid-template-columns: 1.35fr 0.9fr;
            gap: 20px;
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: var(--radius-xl);
            box-shadow: var(--shadow);
            padding: 28px;
          }}

          .badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            border-radius: 999px;
            background: var(--accent-soft);
            color: var(--accent);
            font-size: 13px;
            font-weight: 700;
            padding: 8px 12px;
          }}

          h1 {{
            margin: 14px 0 10px;
            font-size: clamp(32px, 4vw, 48px);
            line-height: 1.08;
            letter-spacing: -0.03em;
          }}

          h2 {{
            margin: 0 0 6px;
            font-size: 26px;
            line-height: 1.18;
          }}

          h3 {{
            margin: 0 0 6px;
            font-size: 18px;
          }}

          p {{ margin: 0; }}
          .muted {{ color: var(--muted); }}

          .chip-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 18px;
          }}

          .chip {{
            border-radius: 999px;
            background: var(--panel-soft);
            border: 1px solid var(--line);
            padding: 10px 14px;
            font-size: 14px;
            font-weight: 600;
            color: #334155;
          }}

          .summary-panel {{
            background: #0f172a;
            color: white;
            border-radius: 24px;
            padding: 22px;
          }}

          .summary-grid {{
            display: grid;
            gap: 10px;
            margin-top: 14px;
          }}

          .summary-item {{
            background: rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 12px 14px;
          }}

          .summary-label {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #94a3b8;
          }}

          .summary-value {{
            margin-top: 4px;
            font-size: 14px;
            line-height: 1.45;
            font-weight: 700;
            word-break: break-word;
          }}

          .error-box {{
            margin-top: 18px;
            border-radius: 18px;
            border: 1px solid #fecaca;
            background: #fff1f2;
            padding: 14px 16px;
            color: #b91c1c;
            font-size: 14px;
            font-weight: 700;
            display: none;
          }}
          .status-notice {{
            margin-top: 14px;
            border-radius: 18px;
            border: 1px solid var(--line);
            padding: 14px 16px;
            font-size: 14px;
            font-weight: 700;
            display: none;
          }}

          .status-notice.success {{
            background: var(--success-soft);
            color: var(--success);
            border-color: #bbf7d0;
          }}

          .status-notice.warning {{
            background: var(--warning-soft);
            color: var(--warning);
            border-color: #fde68a;
          }}

          .status-notice.error {{
            background: var(--danger-soft);
            color: var(--danger);
            border-color: #fecaca;
          }}

          .main-grid {{
            display: grid;
            gap: 20px;
            margin-top: 22px;
            grid-template-columns: 1.18fr 0.82fr;
          }}

          .stack {{
            display: grid;
            gap: 20px;
          }}

          .card {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: var(--radius-xl);
            box-shadow: var(--shadow);
            padding: 24px;
          }}

          .section-head {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 14px;
            margin-bottom: 18px;
          }}

          .button {{
            cursor: pointer;
            border: none;
            border-radius: 16px;
            padding: 13px 16px;
            font-size: 14px;
            font-weight: 800;
            transition: 0.16s ease;
          }}

          .button:hover {{ transform: translateY(-1px); }}
          .button:disabled {{ opacity: 0.55; cursor: not-allowed; transform: none; }}

          .button-primary {{
            background: var(--primary);
            color: white;
          }}

          .button-secondary {{
            background: white;
            color: var(--text);
            border: 1px solid var(--line);
          }}

          .button-accent {{
            background: var(--accent);
            color: white;
          }}

          .form-grid {{
            display: grid;
            gap: 14px;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            padding: 18px;
            background: var(--panel-soft);
            border-radius: 24px;
            margin-bottom: 18px;
          }}

          .field {{
            display: grid;
            gap: 8px;
          }}

          .field.wide {{
            grid-column: 1 / -1;
          }}

          .field span {{
            font-size: 14px;
            font-weight: 700;
            color: #334155;
          }}

          input {{
            width: 100%;
            border: 1px solid #cbd5e1;
            border-radius: 14px;
            padding: 12px 14px;
            font-size: 15px;
            background: white;
            color: var(--text);
          }}

          input:focus {{
            outline: 2px solid rgba(79, 70, 229, 0.18);
            border-color: #818cf8;
          }}

          .action-grid {{
            display: grid;
            gap: 14px;
            grid-template-columns: repeat(2, minmax(0, 1fr));
          }}

          .action-card {{
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 18px;
            background: white;
          }}

          .action-badge {{
            width: 40px;
            height: 40px;
            border-radius: 999px;
            background: #f1f5f9;
            color: #334155;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 800;
            margin-bottom: 12px;
          }}

          .status-pill {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            border: 1px solid transparent;
            padding: 9px 12px;
            font-size: 13px;
            font-weight: 800;
            white-space: nowrap;
          }}

          .status-paid {{
            background: var(--success-soft);
            color: var(--success);
            border-color: #bbf7d0;
          }}

          .status-processing {{
            background: var(--warning-soft);
            color: var(--warning);
            border-color: #fde68a;
          }}

          .status-pending {{
            background: var(--accent-soft);
            color: var(--accent);
            border-color: #c7d2fe;
          }}

          .status-failed {{
            background: var(--danger-soft);
            color: var(--danger);
            border-color: #fecaca;
          }}

          .status-default {{
            background: #f8fafc;
            color: #475569;
            border-color: var(--line);
          }}

          .status-grid {{
            display: grid;
            gap: 14px;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            margin-top: 16px;
          }}

          .status-card {{
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 16px;
            background: white;
          }}

          .status-label {{
            font-size: 13px;
            color: var(--muted);
            font-weight: 700;
          }}

          .status-value {{
            margin-top: 8px;
            font-size: 18px;
            font-weight: 800;
            word-break: break-word;
          }}

          .details-toggle {{
            margin-top: 16px;
            width: 100%;
            text-align: left;
            border: 1px solid var(--line);
            background: var(--panel-soft);
            border-radius: 18px;
            padding: 14px 16px;
            font-weight: 800;
            cursor: pointer;
          }}

          pre {{
            margin: 0;
            white-space: pre-wrap;
            word-break: break-word;
            background: #0f172a;
            color: #e2e8f0;
            padding: 18px;
            border-radius: 0 0 18px 18px;
            overflow-x: auto;
            font-size: 12px;
            line-height: 1.55;
          }}

          .recent-list {{
            display: grid;
            gap: 10px;
            margin-top: 16px;
          }}

          .recent-button {{
            width: 100%;
            text-align: left;
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 14px 16px;
            background: white;
            font-size: 14px;
            font-weight: 700;
            color: #334155;
            cursor: pointer;
          }}

          .recent-button.active {{
            background: var(--accent-soft);
            color: var(--accent);
            border-color: #c7d2fe;
          }}

          .helper-list {{
            margin: 0;
            padding-left: 18px;
          }}

          .info-grid {{
            display: grid;
            gap: 12px;
          }}

          @media (max-width: 1080px) {{
            .hero,
            .main-grid {{
              grid-template-columns: 1fr;
            }}
          }}

          @media (max-width: 760px) {{
            .wrap {{
              padding: 18px 12px 32px;
            }}

            .hero,
            .card {{
              padding: 18px;
            }}

            .form-grid,
            .action-grid,
            .status-grid {{
              grid-template-columns: 1fr;
            }}

            .section-head {{
              flex-direction: column;
              align-items: stretch;
            }}
          }}
        </style>
      </head>
      <body>
        <div class="wrap">
          <section class="hero">
            <div>
              <div class="badge">Live payment integration demo</div>
              <h1>FastAPI payment workflow demo with ECPay callbacks</h1>
              <p class="muted">
                Create a demo order, prepare the ECPay stage checkout, open the hosted payment page in a new window, and watch the final paid state update after server callback confirmation.
              </p>
              <div class="chip-row">
                <div class="chip">Environment: {APP_ENV}</div>
                <div class="chip">Target system: {TARGET_SYSTEM}</div>
                <div class="chip">Storage: <code>{APP_DB_PATH}</code></div>
              </div>
              <div class="chip-row">
                <div class="chip">ECPay stage</div>
                <div class="chip">FastAPI backend</div>
                <div class="chip">SQLite event tracking</div>
                <div class="chip">Slack notification</div>
              </div>
            </div>

            <aside class="summary-panel">
              <div style="font-size:14px;font-weight:700;color:#cbd5e1;">Live summary</div>
              <div class="summary-grid">
                <div class="summary-item">
                  <div class="summary-label">Event ID</div>
                  <div class="summary-value" id="summary_event_id">Not created yet</div>
                </div>
                <div class="summary-item">
                  <div class="summary-label">MerchantTradeNo</div>
                  <div class="summary-value" id="summary_trade_no">—</div>
                </div>
                <div class="summary-item">
                  <div class="summary-label">Status</div>
                  <div class="summary-value" id="summary_status">waiting</div>
                </div>
                <div class="summary-item">
                  <div class="summary-label">Slack</div>
                  <div class="summary-value" id="summary_slack">{"enabled" if SLACK_NOTIFICATIONS_ENABLED else "disabled"}</div>
                </div>
              </div>
            </aside>
          </section>

          <div id="error-box" class="error-box"></div>
          <div id="status-notice" class="status-notice" style="display:none;"></div>

          <section class="main-grid">
            <div class="stack">
              <div class="card">
                <div class="section-head">
                  <div>
                    <h2>Demo flow</h2>
                    <p class="muted">Follow the four-step payment flow below. The checkout opens in a new window so this page can continue tracking the final result.</p>
                  </div>
                  <button class="button button-accent" onclick="resetDemo()">Reset form</button>
                </div>

                <div class="form-grid">
                  <label class="field">
                    <span>Order ID</span>
                    <input id="order_id" />
                  </label>
                  <label class="field">
                    <span>Name</span>
                    <input id="customer_name" value="Alex Chen" />
                  </label>
                  <label class="field wide">
                    <span>Email</span>
                    <input id="customer_email" value="alex@example.com" />
                  </label>
                  <label class="field">
                    <span>Amount (TWD)</span>
                    <input id="amount" type="number" value="499" />
                  </label>
                  <label class="field">
                    <span>Currency</span>
                    <input id="currency" value="TWD" />
                  </label>
                </div>

                <div class="action-grid">
                  <div class="action-card">
                    <div class="action-badge">1</div>
                    <h3>Create order</h3>
                    <p class="muted">Generate a new demo payment event.</p>
                    <button id="create-btn" class="button button-primary" style="margin-top:14px;" onclick="createOrder()">Create order</button>
                  </div>

                  <div class="action-card">
                    <div class="action-badge">2</div>
                    <h3>Prepare checkout</h3>
                    <p class="muted">Build the ECPay stage checkout payload.</p>
                    <button id="prepare-btn" class="button button-primary" style="margin-top:14px;" onclick="startCheckout()">Prepare checkout</button>
                  </div>

                  <div class="action-card">
                    <div class="action-badge">3</div>
                    <h3>Open payment page</h3>
                    <p class="muted">Continue to ECPay and complete the test payment.</p>
                    <button id="open-btn" class="button button-secondary" style="margin-top:14px;" onclick="openPaymentPage()">Open payment</button>
                  </div>

                  <div class="action-card">
                    <div class="action-badge">4</div>
                    <h3>Check final status</h3>
                    <p class="muted">Automatically check the final paid state after the hosted payment flow returns.</p>
                    <button id="status-btn" class="button button-secondary" style="margin-top:14px;" onclick="checkStatus()">Refresh status</button>
                  </div>
                </div>
              </div>

              <div class="card">
                <div class="section-head">
                  <div>
                    <h2>Status area</h2>
                    <p class="muted">This page shows a simple status overview first. Raw event JSON is still available below for technical review.</p>
                  </div>
                  <div id="status-pill" class="status-pill status-default">waiting</div>
                </div>

                <div class="status-grid">
                  <div class="status-card">
                    <div class="status-label">Current state</div>
                    <div class="status-value" id="state_card">Ready</div>
                  </div>
                  <div class="status-card">
                    <div class="status-label">Browser return</div>
                    <div class="status-value" id="browser_card">Pending</div>
                  </div>
                  <div class="status-card">
                    <div class="status-label">Slack notification</div>
                    <div class="status-value" id="slack_card">Pending</div>
                  </div>
                </div>

                <button class="details-toggle" onclick="toggleRaw()">Raw event JSON</button>
                <div id="raw-wrap" style="display:none;">
                  <pre id="result">{{}}</pre>
                </div>
              </div>
            </div>

            <div class="stack">
              <div class="card">
                <h2>Event controls</h2>
                <p class="muted">Keep manual event selection available without making it the first thing users see.</p>

                <div class="form-grid" style="grid-template-columns:1fr; margin-top:18px;">
                  <label class="field">
                    <span>Event ID</span>
                    <input id="event_id" placeholder="evt_xxx" />
                  </label>
                  <label class="field">
                    <span>Status lookup event ID</span>
                    <input id="status_event_id" placeholder="evt_xxx" />
                  </label>
                </div>

                <div class="info-grid">
                  <a class="button button-secondary" href="/docs" style="display:block; text-align:center;">Open Swagger UI</a>
                  <a class="button button-secondary" href="/health" style="display:block; text-align:center;">Health check</a>
                </div>
              </div>

              <div class="card">
                <h2>Recent payment events</h2>
                <p class="muted">Reloading this page does not create a new order. You can reopen or recheck a recent payment event here.</p>
                <div id="recent-events" class="recent-list">
                  <div class="muted">Loading…</div>
                </div>
              </div>

              <div class="card">
                <h2>Demo notes</h2>
                <div class="info-grid">
                  <div><strong>ECPay stage only</strong> · no real payment is processed.</div>
                  <ul class="helper-list">
                    <li>Card: <code>4311-9522-2222-2222</code></li>
                    <li>CVV: <code>222</code></li>
                    <li>Expiry: any future date</li>
                    <li>OTP: <code>1234</code> if prompted</li>
                  </ul>
                  <div>Notification channel: <code>{SLACK_CHANNEL_LABEL}</code></div>
                  <div>Slack notifications: <strong>{"enabled" if SLACK_NOTIFICATIONS_ENABLED else "disabled"}</strong></div>
                  <div><a href="{PUBLIC_BASE_URL}/openapi.json">OpenAPI JSON</a></div>
                </div>
              </div>
            </div>
          </section>
        </div>

        <script>
          let latestPreparedPaymentUrl = "";
          let rawOpen = false;
          let pollingTimer = null;
          const POLL_INTERVAL_MS = 3000;
          const MAX_POLL_ATTEMPTS = 30;
          let pollAttempts = 0;

          
          function stopPolling() {{
            if (pollingTimer) {{
              clearInterval(pollingTimer);
              pollingTimer = null;
            }}
            pollAttempts = 0;
          }}

          function shouldKeepPolling(data) {{
            if (!data) return false;
            return data.status === "payment_processing" || data.status === "redirect_ready";
          }}

          function startPollingStatus(eventId) {{
            stopPolling();
            if (!eventId) return;
            pollAttempts = 0;
            pollingTimer = setInterval(async () => {{
              pollAttempts += 1;
              try {{
                const data = await callJsonApi(`/api/integrations/events/${{eventId}}`, {{ method: "GET" }}, false);
                if (data.event_id) {{
                  setLatestEventId(data.event_id);
                }}
                await loadRecentEvents();
                if (!shouldKeepPolling(data) || pollAttempts >= MAX_POLL_ATTEMPTS) {{
                  stopPolling();
                }}
              }} catch (error) {{
                console.error(error);
                if (pollAttempts >= MAX_POLL_ATTEMPTS) {{
                  stopPolling();
                }}
              }}
            }}, POLL_INTERVAL_MS);
          }}

function generateOrderId() {{
            const now = new Date();
            const pad = (n) => String(n).padStart(2, "0");
            return `DEMO-${{now.getFullYear()}}${{pad(now.getMonth()+1)}}${{pad(now.getDate())}}-${{pad(now.getHours())}}${{pad(now.getMinutes())}}${{pad(now.getSeconds())}}`;
          }}

          function setBusy(buttonId, isBusy, busyText, normalText) {{
            const button = document.getElementById(buttonId);
            if (!button) return;
            button.disabled = isBusy;
            button.textContent = isBusy ? busyText : normalText;
          }}

          function showError(message) {{
            const box = document.getElementById("error-box");
            if (!message) {{
              box.style.display = "none";
              box.textContent = "";
              return;
            }}
            box.style.display = "block";
            box.textContent = message;
          }}

          function showStatusNotice(message, tone = "warning") {{
            const box = document.getElementById("status-notice");
            if (!message) {{
              box.style.display = "none";
              box.className = "status-notice";
              box.textContent = "";
              return;
            }}
            box.style.display = "block";
            box.className = `status-notice ${tone}`;
            box.textContent = message;
          }}

          function updateStatusNotice(data) {{
            if (!data) {{
              showStatusNotice(null);
              return;
            }}
            if (data.status === "paid") {{
              showStatusNotice("Payment confirmed. Final paid state has been verified and polling has stopped.", "success");
              return;
            }}
            if (data.status === "payment_failed") {{
              showStatusNotice("Payment failed. Final status has been received and polling has stopped.", "error");
              return;
            }}
            if (data.status === "payment_processing" || data.status === "redirect_ready") {{
              showStatusNotice("Payment submitted. Waiting for the ECPay server callback to confirm the final result.", "warning");
              return;
            }}
            showStatusNotice(null);
          }}

          function setLatestEventId(eventId) {{
            if (!eventId) return;
            localStorage.setItem("latest_event_id", eventId);
            document.getElementById("event_id").value = eventId;
            document.getElementById("status_event_id").value = eventId;
            document.getElementById("summary_event_id").textContent = eventId;
          }}

          function applyFormDefaults() {{
            document.getElementById("order_id").value = generateOrderId();
            document.getElementById("customer_name").value = "Alex Chen";
            document.getElementById("customer_email").value = "alex@example.com";
            document.getElementById("amount").value = "499";
            document.getElementById("currency").value = "TWD";
          }}

          function statusClass(status) {{
            switch (status) {{
              case "paid": return "status-pill status-paid";
              case "payment_processing": return "status-pill status-processing";
              case "pending_payment":
              case "redirect_ready": return "status-pill status-pending";
              case "payment_failed": return "status-pill status-failed";
              default: return "status-pill status-default";
            }}
          }}

          function updateSummary(data) {{
            document.getElementById("summary_trade_no").textContent = data?.merchant_trade_no || "—";
            document.getElementById("summary_status").textContent = data?.status || "waiting";
            document.getElementById("summary_slack").textContent = data?.notification_status || ({str(SLACK_NOTIFICATIONS_ENABLED).lower()} ? "pending" : "disabled");
          }}

          function updateStatusCards(data) {{
            const status = data?.status || "waiting";
            document.getElementById("status-pill").className = statusClass(status);
            document.getElementById("status-pill").textContent = status;

            let stateText = "Ready";
            if (status === "payment_processing") stateText = "Waiting for server callback";
            else if (status === "paid") stateText = "Confirmed paid";
            else if (status === "redirect_ready") stateText = "Checkout prepared";
            else if (status === "pending_payment") stateText = "Order created";
            else if (status === "payment_failed") stateText = "Payment failed";

            const browserReturned = data?.last_event_type === "ecpay.order_result_url" || data?.last_event_type === "ecpay.return_url";
            const slackState =
              data?.notification_status === "sent"
                ? "Sent"
                : data?.notification_status === "failed"
                  ? "Failed"
                  : ({str(SLACK_NOTIFICATIONS_ENABLED).lower()} ? "Waiting" : "Disabled");

            document.getElementById("state_card").textContent = stateText;
            document.getElementById("browser_card").textContent = browserReturned ? "Received" : "Pending";
            document.getElementById("slack_card").textContent = slackState;
          }}

          function renderResult(data) {{
            document.getElementById("result").textContent = JSON.stringify(data || {{}}, null, 2);
            updateSummary(data);
            updateStatusCards(data);
          }}

          function renderRecentEvents(events) {{
            const container = document.getElementById("recent-events");
            if (!events.length) {{
              container.innerHTML = '<div class="muted">No events yet.</div>';
              return;
            }}
            container.innerHTML = events.map((event) => `
              <button class="recent-button ${{document.getElementById("event_id").value === event.event_id ? "active" : ""}}" onclick="reuseEvent('${{event.event_id}}')">
                <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;">
                  <span style="overflow:hidden;text-overflow:ellipsis;">${{event.event_id}}</span>
                  <span class="muted" style="font-size:12px;">${{event.status}}</span>
                </div>
              </button>
            `).join("");
          }}

          async function loadRecentEvents() {{
            try {{
              const response = await fetch("/api/integrations/events?limit=8");
              const data = await response.json();
              renderRecentEvents(data.events || []);
              if (data.events && data.events.length && !document.getElementById("event_id").value) {{
                setLatestEventId(data.events[0].event_id);
              }}
            }} catch (error) {{
              console.error(error);
            }}
          }}

          function reuseEvent(eventId) {{
            setLatestEventId(eventId);
            checkStatus();
          }}

          async function callJsonApi(url, options, showUiError = true) {{
            const response = await fetch(url, options);
            const data = await response.json();
            renderResult(data);
            if (!response.ok) {{
              if (showUiError) {{
                showError(data.detail || `Request failed (${{response.status}})`);
              }}
              throw new Error(data.detail || `Request failed (${{response.status}})`);
            }}
            return data;
          }}

          async function createOrder() {{
            showError(null);
            setBusy("create-btn", true, "Creating...", "Create order");
            try {{
              stopPolling();
              const payload = {{
                source: "demo_store",
                order_id: document.getElementById("order_id").value || generateOrderId(),
                customer_name: document.getElementById("customer_name").value,
                customer_email: document.getElementById("customer_email").value,
                amount: Number(document.getElementById("amount").value),
                currency: document.getElementById("currency").value,
              }};
              const data = await callJsonApi("/api/integrations/orders", {{
                method: "POST",
                headers: {{ "Content-Type": "application/json" }},
                body: JSON.stringify(payload),
              }});
              if (data.event_id) {{
                setLatestEventId(data.event_id);
                applyFormDefaults();
                latestPreparedPaymentUrl = "";
                await loadRecentEvents();
              }}
            }} catch (error) {{
              showError(error.message || "Create order failed.");
            }} finally {{
              setBusy("create-btn", false, "Creating...", "Create order");
            }}
          }}

          async function startCheckout() {{
            showError(null);
            const eventId = document.getElementById("event_id").value;
            if (!eventId) {{
              showError("Enter or select an event ID first.");
              return;
            }}
            setBusy("prepare-btn", true, "Preparing...", "Prepare checkout");
            try {{
              const data = await callJsonApi("/api/payments/ecpay/checkout", {{
                method: "POST",
                headers: {{ "Content-Type": "application/json" }},
                body: JSON.stringify({{ event_id: eventId }}),
              }});
              if (data.event_id) {{
                setLatestEventId(data.event_id);
              }}
              latestPreparedPaymentUrl = data.payment_page_url || "";
              if (latestPreparedPaymentUrl) {{
                document.getElementById("open-btn").className = "button button-primary";
              }}
              await loadRecentEvents();
            }} catch (error) {{
              showError(error.message || "Prepare checkout failed.");
            }} finally {{
              setBusy("prepare-btn", false, "Preparing...", "Prepare checkout");
            }}
          }}

          function openPaymentPage() {{
            showError(null);
            if (!latestPreparedPaymentUrl) {{
              showError("Prepare checkout first.");
              return;
            }}
            const eventId = document.getElementById("event_id").value || document.getElementById("status_event_id").value;
            const popup = window.open(latestPreparedPaymentUrl, "_blank", "noopener,noreferrer");
            if (!popup) {{
              showError("The payment page was blocked by the browser popup setting. Please allow popups and try again.");
              return;
            }}
            popup.focus();
            if (eventId) {{
              startPollingStatus(eventId);
            }}
          }}
            const popup = window.open(latestPreparedPaymentUrl, "_blank", "noopener,noreferrer");
            if (!popup) {{
              showError("The payment page was blocked by the browser popup setting. Please allow popups and try again.");
              return;
            }}
            popup.focus();
          }}

          async function checkStatus() {{
            showError(null);
            stopPolling();
            const eventId = document.getElementById("status_event_id").value || document.getElementById("event_id").value;
            if (!eventId) {{
              showError("Enter or select an event ID first.");
              return;
            }}
            setBusy("status-btn", true, "Refreshing...", "Refresh status");
            try {{
              const data = await callJsonApi(`/api/integrations/events/${{eventId}}`, {{ method: "GET" }});
              if (data.event_id) {{
                setLatestEventId(data.event_id);
              }}
              await loadRecentEvents();
            }} catch (error) {{
              showError(error.message || "Get event status failed.");
            }} finally {{
              setBusy("status-btn", false, "Refreshing...", "Refresh status");
            }}
          }}

          function toggleRaw() {{
            rawOpen = !rawOpen;
            document.getElementById("raw-wrap").style.display = rawOpen ? "block" : "none";
          }}

          function resetDemo() {{
            stopPolling();
            applyFormDefaults();
            showError(null);
            showStatusNotice(null);
            latestPreparedPaymentUrl = "";
            document.getElementById("event_id").value = "";
            document.getElementById("status_event_id").value = "";
            document.getElementById("summary_event_id").textContent = "Not created yet";
            document.getElementById("summary_trade_no").textContent = "—";
            document.getElementById("summary_status").textContent = "waiting";
            document.getElementById("summary_slack").textContent = ({str(SLACK_NOTIFICATIONS_ENABLED).lower()} ? "pending" : "disabled");
            document.getElementById("state_card").textContent = "Ready";
            document.getElementById("browser_card").textContent = "Pending";
            document.getElementById("slack_card").textContent = ({str(SLACK_NOTIFICATIONS_ENABLED).lower()} ? "Waiting" : "Disabled");
            document.getElementById("status-pill").className = "status-pill status-default";
            document.getElementById("status-pill").textContent = "waiting";
            document.getElementById("result").textContent = "{{}}";
            document.getElementById("open-btn").className = "button button-secondary";
            localStorage.removeItem("latest_event_id");
            loadRecentEvents();
          }}

          applyFormDefaults();
          document.getElementById("result").textContent = "{{}}";
          const latestEventId = localStorage.getItem("latest_event_id");
          if (latestEventId) setLatestEventId(latestEventId);
          updateStatusCards(null);
          showStatusNotice(null);
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
