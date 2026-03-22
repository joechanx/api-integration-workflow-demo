# API Integration Workflow Demo

A minimal FastAPI project that demonstrates a practical API integration workflow.

This demo shows how external order data can be received, validated, mapped into an internal format, processed through a simulated downstream system, and tracked by integration event status. 

## What this project demonstrates
- API request handling with FastAPI
- Input validation with Pydantic
- Payload mapping between external and internal systems
- Webhook-style callback flow
- Integration event status tracking
- Clean and maintainable backend structure

## Demo scenario
This project simulates a common business workflow:
1. An external platform sends order data
2. The backend validates the request
3. The payload is mapped into an internal ERP-friendly format
4. A downstream system processes the request
5. The result is stored and can be queried by event ID

## Main endpoints
- `GET /`
- `GET /health`
- `POST /api/integrations/orders`
- `POST /api/integrations/webhooks/erp`
- `GET /api/integrations/events/{event_id}`

## Tech stack
- Python
- FastAPI
- Pydantic
- Pytest
- Railway-ready deployment config