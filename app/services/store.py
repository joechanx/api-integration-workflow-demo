import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any

from app.core.config import APP_DB_PATH
from app.models import EventRecord, MappedOrder


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EventStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._conn:
            self._conn.execute("PRAGMA journal_mode=WAL;")
            self._conn.execute("PRAGMA synchronous=NORMAL;")
        self._create_tables()

    def _create_tables(self) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    status TEXT NOT NULL,
                    target_system TEXT NOT NULL,
                    mapped_payload_json TEXT NOT NULL,
                    payment_page_url TEXT,
                    merchant_trade_no TEXT UNIQUE,
                    ecpay_trade_no TEXT,
                    payment_type TEXT,
                    rtn_code INTEGER,
                    rtn_msg TEXT,
                    last_event_type TEXT,
                    message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def save(self, event: EventRecord) -> EventRecord:
        row = self._event_to_row(event)
        with self._lock, self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO events (
                    event_id, source, status, target_system, mapped_payload_json,
                    payment_page_url, merchant_trade_no, ecpay_trade_no, payment_type,
                    rtn_code, rtn_msg, last_event_type, message, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(row.values()),
            )
        return event

    def get(self, event_id: str) -> EventRecord | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM events WHERE event_id = ?", (event_id,)
            ).fetchone()
        return self._row_to_event(row) if row else None

    def get_by_merchant_trade_no(self, merchant_trade_no: str) -> EventRecord | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM events WHERE merchant_trade_no = ?", (merchant_trade_no,)
            ).fetchone()
        return self._row_to_event(row) if row else None

    def update(self, event_id: str, event: EventRecord) -> EventRecord:
        existing = self.get(event_id)
        created_at = existing.created_at if existing else event.created_at
        updated = event.model_copy(update={"created_at": created_at, "updated_at": _utc_now_iso()})
        return self.save(updated)

    def list_recent(self, limit: int = 5) -> list[EventRecord]:
        safe_limit = max(1, min(limit, 20))
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM events ORDER BY updated_at DESC, created_at DESC LIMIT ?",
                (safe_limit,),
            ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def clear(self) -> None:
        with self._lock, self._conn:
            self._conn.execute("DELETE FROM events")

    def _event_to_row(self, event: EventRecord) -> dict[str, Any]:
        return {
            "event_id": event.event_id,
            "source": event.source,
            "status": event.status,
            "target_system": event.target_system,
            "mapped_payload_json": event.mapped_payload.model_dump_json(),
            "payment_page_url": event.payment_page_url,
            "merchant_trade_no": event.merchant_trade_no,
            "ecpay_trade_no": event.ecpay_trade_no,
            "payment_type": event.payment_type,
            "rtn_code": event.rtn_code,
            "rtn_msg": event.rtn_msg,
            "last_event_type": event.last_event_type,
            "message": event.message,
            "created_at": event.created_at,
            "updated_at": event.updated_at,
        }

    def _row_to_event(self, row: sqlite3.Row) -> EventRecord:
        payload = MappedOrder.model_validate(json.loads(row["mapped_payload_json"]))
        return EventRecord(
            event_id=row["event_id"],
            source=row["source"],
            status=row["status"],
            target_system=row["target_system"],
            mapped_payload=payload,
            payment_page_url=row["payment_page_url"],
            merchant_trade_no=row["merchant_trade_no"],
            ecpay_trade_no=row["ecpay_trade_no"],
            payment_type=row["payment_type"],
            rtn_code=row["rtn_code"],
            rtn_msg=row["rtn_msg"],
            last_event_type=row["last_event_type"],
            message=row["message"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


event_store = EventStore(APP_DB_PATH)
