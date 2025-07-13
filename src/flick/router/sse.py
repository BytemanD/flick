import json

import tornado
from loguru import logger

from flick.router import basehandler
from flick.service import sse


class SSE(basehandler.BaseRequestHandler):

    def _send_event(self, request: tornado.web.RequestHandler, event: sse.Event):
        message = f"data: {json.dumps(event.to_json())}\n\n"
        request.write(message)

    async def get(self):
        session_id = self.get_argument("session_id", "")
        if not session_id:
            self.finish_badrequest({"error": "channel_id is required"})
            return
        logger.info("receive sse connection")

        self.set_header("Content-Type", "text/event-stream")
        self.set_header("Cache-Control", "no-cache")
        self.set_header("Connection", "keep-alive")

        channel = sse.SSE_SERVICE.new_channel(session_id)
        await channel.send_event("sse connected", level="success")
        while True:
            event = await channel.get()
            logger.debug("receive event from {}[{}]: {}", channel, channel.size(), event.to_json())
            message = f"data: {json.dumps(event.to_json())}\n\n"
            self.write(message)
            self.flush()
            # logger.debug("sent event {}: {}", channel, event.to_json())

    def on_connection_close(self):
        logger.warning("sse 链接断开")
