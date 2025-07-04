import json

import flask
from flask_restful import Resource
from loguru import logger

from flick.service import sse


class SSE(Resource):

    def get(self):
        session_id = flask.request.args.get('session_id')
        if not session_id:
            return {'error': 'channel_id is required'}, 403
        channel = sse.SSE_SERVICE.get_channel(session_id)
        sse.SSE_SERVICE.send_connected_event()
        logger.info("receive sse connection")

        def event_stream():
            while True:
                event = channel.get()
                logger.debug(
                    "send event to channel {}: {}", channel.session_id, event.to_json()
                )
                yield f"data: {json.dumps(event.to_json())}\n\n"

        return flask.Response(
            event_stream(),
            mimetype="text/event-stream",
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
