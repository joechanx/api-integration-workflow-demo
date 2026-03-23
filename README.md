# API Integration Workflow Demo with Stripe Test Checkout

A minimal FastAPI project that demonstrates a practical payment integration workflow.

This version is prepared for direct deployment from GitHub to Railway so you can share a live demo link with clients.

![Portfolio cover](docs/portfolio-cover.png)

Open:

- [Home](https://api-integration-workflow-demo-production.up.railway.app/)
- [Swagger UI](https://api-integration-workflow-demo-production.up.railway.app/docs)
  
## What this project demonstrates

- API request handling with FastAPI
- Input validation with Pydantic
- Payload mapping between external and internal systems
- Stripe Checkout Session creation in test mode
- Stripe webhook signature verification
- Payment status tracking by event ID
- Railway-ready deployment config

## Demo scenario

1. A client creates a demo order.
2. The backend validates and stores the order with `pending_payment` status.
3. The backend creates a Stripe Checkout Session in test mode.
4. The client completes payment on Stripe's hosted checkout page.
5. Stripe sends webhook events to the backend.
6. The backend updates the event status.
7. The client checks the final result through the status endpoint.

## Project structure

```text
api-integration-workflow-demo/
├─ app/
│  ├─ core/
│  │  └─ config.py
│  ├─ routers/
│  │  ├─ integrations.py
│  │  └─ payments.py
│  ├─ services/
│  │  ├─ mapper.py
│  │  ├─ processor.py
│  │  ├─ store.py
│  │  └─ stripe_gateway.py
│  ├─ main.py
│  └─ models.py
├─ docs/
│  └─ portfolio-cover.png
├─ tests/
│  ├─ conftest.py
│  └─ test_integrations.py
├─ .env.example
├─ railway.json
├─ README.md
├─ requirements.txt
└─ .gitignore
```

## Main endpoints

- `GET /`
- `GET /health`
- `POST /api/integrations/orders`
- `POST /api/payments/checkout-session`
- `POST /api/integrations/webhooks/stripe`
- `GET /api/integrations/events/{event_id}`
- `GET /payments/success`
- `GET /payments/cancel`

## Stripe test mode

No real payment is processed.

Recommended test card:

- Card number: `4242 4242 4242 4242`
- Expiry date: any future date
- CVC: any 3 digits
- Postal code: any value

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
- Test-mode Stripe Checkout implementation
- Webhook verification and event handling
- Clean backend service structure
- A live cloud demo that clients can test without local setup
