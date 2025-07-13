import asyncio
import dataclasses
from typing import Dict

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

    def __str__(self) -> str:
        return f"<Event '{self.name}'>"


def new_event(name, detail="", level="info", item=None) -> Event:
    return Event(name=name, level=level, detail=detail, item=item or {})


class Channel:

    def __init__(self, session_id) -> None:
        self.session_id = session_id
        self.events = asyncio.Queue()

    def __str__(self) -> str:
        return f"Channel({id(self)} sid: {self.session_id})"

    def size(self):
        return self.events.qsize()

    # def event_stream(self):
    #     while True:
    #         event = self.events.get()
    #         yield f"data: {json.dumps(event)}\n\n"

    async def put(self, event: Event):
        logger.debug("{} (queue: {}) put event: {}", self, id(self.events), event)
        await self.events.put(event)

    async def get(self) -> Event:
        return await self.events.get()  # type: ignore

    def empty(self) -> bool:
        return self.events.empty()

    async def send_event(self, event_name: str, level=None, detail=None, item=None):
        event = Event(
            name=event_name,
            level=level or "info",
            detail=detail or "",
            item=item or {},
        )
        await self.put(event)


class SSEService:

    def __init__(self) -> None:
        self.channels: Dict[str, Channel] = {}

    def get_channel(self, session_id) -> Channel:
        if session_id not in self.channels:
            self.new_channel(session_id)
        return self.channels[session_id]

    def new_channel(self, session_id) -> Channel:
        logger.info("new channel with session_id {}", session_id)
        self.channels[session_id] = Channel(session_id)
        return self.channels[session_id]

    def remove_channel(self, session_id):
        logger.info("remove channel for session {}", session_id)
        self.channels.pop(session_id, None)

    async def send_connected_event(self, session_id):
        await self.get_channel(session_id).send_event("sse connected", level="success")


SSE_SERVICE = SSEService()
