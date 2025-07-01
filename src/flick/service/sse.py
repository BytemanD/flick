import time
import uuid
import dataclasses
from typing import Dict
import json
import queue

import flask
from flask import session
from loguru import logger


@dataclasses.dataclass
class Event:
    level: str
    title: str
    detail: str = ""
    item: dict = dataclasses.field(default_factory=dict)
    timestramp: float = 0

    def to_json(self):
        return dataclasses.asdict(self)


def new_event(level, title, detail, item={}) -> Event:
    return Event(level=level, title=title, detail=detail, item=item)

class Channel:

    def __init__(self) -> None:
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

    def get_channel(self) -> Channel:
        sid: str = session.get("id") or uuid.uuid4().hex

        if sid not in self.channels:
            logger.info("new channel for session {}", sid)
            self.channels[sid] = Channel()
        self.send_connected(sid)
        return self.channels[sid]

    def send_event(self, sid: str, event: Event):
        self.channels[sid].put(event)
        logger.debug("send event to session {}: {}", sid, event)

    def send_connected(self, sid):
        self.send_event(sid, new_event("success", "connected", '', {}))

    def get_session_id(self):
        return session.get("id")


SSE_SERVICE = SSEService()


def connect():
    channel = SSE_SERVICE.get_channel()

    def event_stream():
        while True:
            event = channel.get()
            yield f"data: {json.dumps(event.to_json())}\n"

    return flask.Response(
        event_stream(),
        mimetype="text/event-stream",
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
