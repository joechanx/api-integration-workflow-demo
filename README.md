# API Integration Workflow Demo (Railway-ready)

A minimal FastAPI project that demonstrates API request handling, payload mapping, webhook-style callback flow, basic validation, and event status tracking.

This version is prepared for **direct deployment from GitHub to Railway**, so you can share a live demo link with clients.

![Portfolio cover](docs/portfolio-cover.png)

## Why this project exists

This demo was created as a lightweight portfolio project for backend integration work. It focuses on a simple but realistic workflow:

1. Receive order data from an external platform.
2. Validate the request.
3. Map the external payload into an internal format.
4. Store the integration event.
5. Simulate downstream completion through a webhook callback.
6. Query the final status.

## Demo scenario

An external e-commerce platform sends an order into the backend. The backend converts the payload into an ERP-friendly format, keeps a status record, and waits for a webhook-style callback from the target system.

## Tech stack

- Python
- FastAPI
- Pydantic
- Pytest
- Railway

## Project structure

```text
api-integration-workflow-demo/
├─ app/
│  ├─ main.py
│  ├─ models.py
│  ├─ core/
│  │  └─ config.py
│  ├─ routers/
│  │  └─ integrations.py
│  └─ services/
│     ├─ mapper.py
│     ├─ processor.py
│     └─ store.py
├─ docs/
│  └─ portfolio-cover.png
├─ tests/
│  └─ test_integrations.py
├─ .env.example
├─ railway.json
├─ README.md
├─ requirements.txt
└─ .gitignore
```

## Features

- REST API with FastAPI
- Input validation with Pydantic
- Payload mapping between external and internal schemas
- Webhook-style callback endpoint
- Event status lookup
- Minimal automated tests
- Root landing page for client-friendly live demo sharing
- Railway config-as-code via `railway.json`

## API endpoints

### 1. Landing page

`GET /`

Shows a simple HTML page with links to Swagger UI and quick testing instructions.

### 2. Health check

`GET /health`

Response:

```json
{
  "status": "ok"
}
```

### 3. Create integration event

`POST /api/integrations/orders`

Request:

```json
{
  "source": "shopify",
  "order_id": "SHP-1001",
  "customer_name": "Alex Chen",
  "customer_email": "alex@example.com",
  "amount": 1299,
  "currency": "TWD"
}
```

Response:

```json
{
  "event_id": "evt_0001",
  "status": "received",
  "target_system": "mock_erp",
  "mapped_payload": {
    "external_order_id": "SHP-1001",
    "client_name": "Alex Chen",
    "client_email": "alex@example.com",
    "total_amount": 1299,
    "currency": "TWD",
    "source_platform": "shopify"
  },
  "webhook_hint": "POST /api/integrations/webhooks/erp"
}
```

### 4. Simulated ERP webhook callback

`POST /api/integrations/webhooks/erp`

Request:

```json
{
  "event_id": "evt_0001",
  "result": "processed",
  "reference_id": "ERP-2026-0001",
  "message": "Order synced successfully"
}
```

### 5. Query integration event

`GET /api/integrations/events/{event_id}`

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

Open:

- Home: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`

## Run tests

```bash
pytest
```

## Deploy to Railway from GitHub

1. Push this repo to GitHub.
2. In Railway, create a new project.
3. Choose **Deploy from GitHub repo**.
4. Select this repository.
5. After the deploy finishes, go to **Settings -> Networking** and click **Generate Domain**.
6. Add the generated public URL to the `PUBLIC_BASE_URL` variable in Railway.
7. Redeploy once so the landing page shows the correct public OpenAPI URL.

## Suggested Railway variables

You can import these from `.env.example`:

```env
APP_NAME=API Integration Workflow Demo
APP_ENV=production
TARGET_SYSTEM=mock_erp
PUBLIC_BASE_URL=https://your-service-name.up.railway.app
```

## Why `railway.json` is included

This repository uses `railway.json` so the start command is versioned with the codebase and works immediately after GitHub import.

The app starts with:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## What this project showcases

- Backend workflow design
- API integration structure
- Request and response handling
- Simple validation and mapping logic
- A clean, reusable FastAPI codebase for portfolio display
- A live cloud demo that clients can test without local setup
