import json

from loguru import logger
import tornado

from flick.router import basehandler
from flick.service import sse

class SSE(basehandler.BaseRequestHandler):

    async def get(self):
        session_id = self.get_argument("session_id", "")
        if not session_id:
            self.finish_badrequest({"error": "channel_id is required"})
            return
        channel = sse.SSE_SERVICE.get_channel(session_id)

        logger.info("receive sse connection")

        self.set_header("Content-Type", "text/event-stream")
        self.set_header("Cache-Control", "no-cache")
        self.set_header("Connection", "keep-alive")

        channel.send_event("sse connected", level="success")

        while True:
            event = await channel.get()
            logger.debug("send event to channel {}: {}", channel.session_id, event.to_json())
            message = f"data: {json.dumps(event.to_json())}\n\n"
            self.write(message)
            self.flush()
