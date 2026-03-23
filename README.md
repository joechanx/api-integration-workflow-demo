# API Integration Workflow Demo with ECPay Stage Checkout

A minimal FastAPI project that demonstrates a practical payment integration workflow.

This version is prepared for direct deployment from GitHub to Railway so you can share a live demo link with clients. It upgrades the earlier demo by storing events in SQLite, using UUID-based event IDs, and changing the ECPay result page to a reload-safe POST → Redirect → GET flow.

## Live Demo

- **Demo URL:** [Home](https://api-integration-workflow-demo-production.up.railway.app/)
- **Demo URL:** [Swagger UI](https://api-integration-workflow-demo-production.up.railway.app/docs)

![Portfolio cover](docs/portfolio-cover.png)

## What this project demonstrates

- API request handling with FastAPI
- Input validation with Pydantic
- Payload mapping between external and internal systems
- ECPay stage credit checkout form generation
- CheckMacValue generation and callback verification
- Browser return handling with reload-safe status polling
- Payment status tracking by UUID-based event ID
- SQLite persistence for demo stability on Railway
- Railway-ready deployment config

## Why this v4 update matters

The previous in-memory demo could lose state after a Railway restart and could confuse users when a browser reload created a new event flow. This version fixes that by:

- storing events in `data/demo.db`
- generating globally unique `event_id` values
- keeping `event_id` in the result page URL
- surfacing recent events on the home page
- letting users resume status checks for the same payment after reloads

## Demo scenario

1. A client creates a demo order.
2. The backend validates and stores the order with `pending_payment` status.
3. The backend prepares an ECPay stage credit checkout form.
4. The client completes payment on ECPay's hosted checkout page.
5. The browser returns to a reload-safe result page that keeps polling for the latest status.
6. ECPay sends a server-side callback to the backend.
7. The backend verifies the callback and updates the event status in SQLite.
8. The result page and home page recent-event table both show the final state.

## Main endpoints

- `GET /`
- `GET /health`
- `POST /api/integrations/orders`
- `GET /api/integrations/events?limit=8`
- `GET /api/integrations/events/{event_id}`
- `POST /api/payments/ecpay/checkout`
- `POST /api/integrations/webhooks/ecpay/return`
- `GET /payments/ecpay/redirect/{event_id}`
- `POST /payments/ecpay/result`
- `GET /payments/ecpay/result?event_id=...`
- `GET /payments/ecpay/back`

## ECPay stage environment

No real payment is processed.

Recommended stage test values:

- Card number: `4311-9522-2222-2222`
- CVV: `222`
- Expiry date: any future date
- OTP: `1234` if prompted
- Currency: `TWD` only

## Run locally

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run tests

```bash
pytest
```

## What this project showcases

- Payment integration workflow design
- Hosted checkout redirection with a Taiwanese payment provider
- Callback verification and event handling
- Practical fixes for async callback UX in demos
- Reload-safe result tracking
- Stable cloud demo behavior with SQLite persistence
