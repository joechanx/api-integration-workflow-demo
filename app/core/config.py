import os
from pathlib import Path


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


APP_NAME = os.getenv("APP_NAME", "API Integration Workflow Demo")
APP_ENV = os.getenv("APP_ENV", "development")
TARGET_SYSTEM = os.getenv("TARGET_SYSTEM", "ecpay_stage_credit")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
DATA_DIR.mkdir(parents=True, exist_ok=True)
APP_DB_PATH = os.getenv("APP_DB_PATH", str(DATA_DIR / "demo.db"))

ECPAY_ENV = os.getenv("ECPAY_ENV", "stage")
ECPAY_MERCHANT_ID = os.getenv("ECPAY_MERCHANT_ID", "3002607")
ECPAY_HASH_KEY = os.getenv("ECPAY_HASH_KEY", "pwFHCqoQZGmho4w6")
ECPAY_HASH_IV = os.getenv("ECPAY_HASH_IV", "EkRm7iFT261dpevs")
ECPAY_CHECKOUT_URL = os.getenv(
    "ECPAY_CHECKOUT_URL",
    "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5",
)

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "").strip()
SLACK_NOTIFICATIONS_ENABLED = _env_flag(
    "SLACK_NOTIFICATIONS_ENABLED",
    default=bool(SLACK_WEBHOOK_URL),
)
SLACK_CHANNEL_LABEL = os.getenv("SLACK_CHANNEL_LABEL", "demo Slack channel")
