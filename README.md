# API Integration Workflow Demo with ECPay Stage Checkout

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
- ECPay stage credit checkout form generation
- CheckMacValue generation and callback verification
- Payment status tracking by event ID
- Railway-ready deployment config

## Demo scenario

1. A client creates a demo order.
2. The backend validates and stores the order with `pending_payment` status.
3. The backend prepares an ECPay stage credit checkout form.
4. The client completes payment on ECPay's hosted checkout page.
5. ECPay sends a server-side callback to the backend.
6. The backend verifies the callback and updates the event status.
7. The client checks the final result through the status endpoint.

## Project structure

```text
api-integration-workflow-demo/
├─ app/
│  ├─ core/
│  │  └─ config.py
│  ├─ routers/
│  │  ├─ integrations.py
│  │  └─ payments_ecpay.py
│  ├─ services/
│  │  ├─ ecpay_checkmac.py
│  │  ├─ ecpay_service.py
│  │  ├─ mapper.py
│  │  ├─ processor.py
│  │  └─ store.py
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
- `POST /api/payments/ecpay/checkout`
- `POST /api/integrations/webhooks/ecpay/return`
- `GET /api/integrations/events/{event_id}`
- `GET /payments/ecpay/redirect/{event_id}`
- `POST /payments/ecpay/result`
- `GET /payments/ecpay/back`

## ECPay stage environment

No real payment is processed.

Recommended stage test card:

- Card number: `4311-9522-2222-2222`
- CVV: `222`
- Expiry date: any future date
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
- Clean backend service structure
- A live cloud demo that clients can test without local setup
