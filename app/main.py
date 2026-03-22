from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.core.config import APP_ENV, APP_NAME, PUBLIC_BASE_URL, TARGET_SYSTEM
from app.routers.integrations import router as integrations_router

app = FastAPI(
    title=APP_NAME,
    version="0.2.0",
    description=(
        "A minimal FastAPI demo that showcases request validation, payload mapping, "
        "webhook-style callbacks, and event status tracking."
    ),
)


@app.get("/", tags=["system"], response_class=HTMLResponse)
def home() -> str:
    docs_url = "/docs"
    health_url = "/health"
    sample_create_url = "/api/integrations/orders"
    sample_webhook_url = "/api/integrations/webhooks/erp"

    return f"""
    <!doctype html>
    <html lang=\"en\">
      <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>{APP_NAME}</title>
        <style>
          body {{ font-family: Arial, sans-serif; max-width: 860px; margin: 40px auto; padding: 0 16px; line-height: 1.6; }}
          code, pre {{ background: #f5f5f5; padding: 2px 6px; border-radius: 6px; }}
          pre {{ padding: 12px; overflow-x: auto; }}
          .card {{ border: 1px solid #ddd; border-radius: 12px; padding: 18px; margin: 16px 0; }}
          a {{ text-decoration: none; }}
        </style>
      </head>
      <body>
        <h1>{APP_NAME}</h1>
        <p>Environment: <strong>{APP_ENV}</strong></p>
        <p>Target system: <strong>{TARGET_SYSTEM}</strong></p>
        <p>This is a live backend demo for API integration workflow testing.</p>

        <div class=\"card\">
          <h2>Useful links</h2>
          <ul>
            <li><a href=\"{docs_url}\">Swagger UI</a></li>
            <li><a href=\"{health_url}\">Health check</a></li>
            <li><a href=\"{PUBLIC_BASE_URL}/openapi.json\">OpenAPI JSON</a></li>
          </ul>
        </div>

        <div class=\"card\">
          <h2>How to test</h2>
          <ol>
            <li>Open <a href=\"{docs_url}\">Swagger UI</a>.</li>
            <li>Run <code>POST {sample_create_url}</code>.</li>
            <li>Copy the returned <code>event_id</code>.</li>
            <li>Run <code>POST {sample_webhook_url}</code> with that <code>event_id</code>.</li>
            <li>Run <code>GET /api/integrations/events/{{event_id}}</code> to confirm final status.</li>
          </ol>
        </div>

        <div class=\"card\">
          <h2>Sample payload</h2>
          <pre>{{
  \"source\": \"shopify\",
  \"order_id\": \"SHP-1001\",
  \"customer_name\": \"Alex Chen\",
  \"customer_email\": \"alex@example.com\",
  \"amount\": 1299,
  \"currency\": \"TWD\"
}}</pre>
        </div>
      </body>
    </html>
    """


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(integrations_router)
