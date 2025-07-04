import dataclasses
import json
import queue
from typing import Dict

import flask
from loguru import logger


@dataclasses.dataclass
class Event:
    name: str
    level: str = "info"
    detail: str = ""
    item: dict = dataclasses.field(default_factory=dict)
    timestramp: float = 0

    def to_json(self):
        return dataclasses.asdict(self)


def new_event(name, detail="", level="info", item=None) -> Event:
    return Event(name=name, level=level, detail=detail, item=item or {})


class Channel:

    def __init__(self, session_id) -> None:
        self.session_id = session_id
        self.events = queue.Queue()

    def event_stream(self):
        while True:
            event = self.events.get()
            yield f"data: {json.dumps(event)}\n"

    def put(self, event: Event):
        self.events.put(event)

    def get(self) -> Event:
        return self.events.get()


class SSEService:

    def __init__(self) -> None:
        self.channels: Dict[str, Channel] = {}

    def _get_session_id(self) -> str:
        if "id" not in flask.session:
            raise RuntimeError("session id is none")
        return flask.session.get("id", "")

    def get_channel(self, session_id) -> Channel:
        if session_id not in self.channels:
            logger.info("new channel with session_id {}", session_id)
            self.channels[session_id] = Channel(session_id)
        return self.channels[session_id]

    def send_event(self, event_name: str, level=None, detail=None, item=None):
        event = Event(
            name=event_name,
            level=level or "info",
            detail=detail or "",
            item=item or {},
        )
        self.get_channel(self._get_session_id()).put(event)

    def send_connected_event(self):
        self.send_event("sse connected", level="success")


SSE_SERVICE = SSEService()
