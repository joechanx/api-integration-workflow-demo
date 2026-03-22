from app.models import EventRecord


class EventStore:
    def __init__(self) -> None:
        self._events: dict[str, EventRecord] = {}
        self._counter = 0

    def next_event_id(self) -> str:
        self._counter += 1
        return f"evt_{self._counter:04d}"

    def save(self, event: EventRecord) -> EventRecord:
        self._events[event.event_id] = event
        return event

    def get(self, event_id: str) -> EventRecord | None:
        return self._events.get(event_id)

    def update(self, event_id: str, event: EventRecord) -> EventRecord:
        self._events[event_id] = event
        return event

    def clear(self) -> None:
        self._events.clear()
        self._counter = 0


event_store = EventStore()
