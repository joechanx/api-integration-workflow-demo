import hashlib
from urllib.parse import quote_plus

from app.core.config import ECPAY_HASH_IV, ECPAY_HASH_KEY


_REPLACE_TABLE = {
    "%2d": "-",
    "%5f": "_",
    "%2e": ".",
    "%21": "!",
    "%2a": "*",
    "%28": "(",
    "%29": ")",
    "%20": "+",
}


def _ecpay_url_encode(value: str) -> str:
    encoded = quote_plus(value, safe="-_.!*()")
    lower = encoded.lower()
    for source, target in _REPLACE_TABLE.items():
        lower = lower.replace(source, target)
    return lower


def generate_check_mac_value(parameters: dict[str, str | int]) -> str:
    sanitized = {
        key: "" if value is None else str(value)
        for key, value in parameters.items()
        if key != "CheckMacValue"
    }
    sorted_items = sorted(sanitized.items(), key=lambda item: item[0].lower())
    query = "&".join(f"{key}={value}" for key, value in sorted_items)
    raw = f"HashKey={ECPAY_HASH_KEY}&{query}&HashIV={ECPAY_HASH_IV}"
    encoded = _ecpay_url_encode(raw)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()


def verify_check_mac_value(parameters: dict[str, str]) -> bool:
    provided = parameters.get("CheckMacValue", "")
    if not provided:
        return False
    expected = generate_check_mac_value(parameters)
    return expected == provided.upper()
