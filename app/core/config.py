import os

APP_NAME = os.getenv("APP_NAME", "API Integration Workflow Demo")
APP_ENV = os.getenv("APP_ENV", "development")
TARGET_SYSTEM = os.getenv("TARGET_SYSTEM", "ecpay_stage_credit")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

ECPAY_ENV = os.getenv("ECPAY_ENV", "stage")
ECPAY_MERCHANT_ID = os.getenv("ECPAY_MERCHANT_ID", "3002607")
ECPAY_HASH_KEY = os.getenv("ECPAY_HASH_KEY", "pwFHCqoQZGmho4w6")
ECPAY_HASH_IV = os.getenv("ECPAY_HASH_IV", "EkRm7iFT261dpevs")
ECPAY_CHECKOUT_URL = os.getenv(
    "ECPAY_CHECKOUT_URL",
    "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5",
)
