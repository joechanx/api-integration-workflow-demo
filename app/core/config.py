import os

APP_NAME = os.getenv("APP_NAME", "API Integration Workflow Demo")
APP_ENV = os.getenv("APP_ENV", "development")
TARGET_SYSTEM = os.getenv("TARGET_SYSTEM", "stripe_checkout")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
