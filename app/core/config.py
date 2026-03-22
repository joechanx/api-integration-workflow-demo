import os

APP_NAME = os.getenv("APP_NAME", "API Integration Workflow Demo")
APP_ENV = os.getenv("APP_ENV", "development")
TARGET_SYSTEM = os.getenv("TARGET_SYSTEM", "mock_erp")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")
