import dataclasses
import json
import uuid
from concurrent import futures
from functools import lru_cache
from typing import Optional, Union

import jsonschema
import jwt
import tornado
from tornado import web
from tornado.concurrent import Future

from flick.common import context
from flick.service import sse


def make_session_id():
    return f"sid-{uuid.uuid4()}"


def make_request_id():
    return f"req-{uuid.uuid4()}"


class BaseRequestHandler(web.RequestHandler):
    executor = futures.ThreadPoolExecutor()

    auth_required = False
    auth_methods = ["GET", "POST", "PUT", "DELETE"]

    def prepare(self):
        super().prepare()
        if not self.get_cookie("sid"):
            self.set_cookie("sid", make_session_id())
        if not self.request.headers.get("X-Request-ID"):
            self.request.headers.setdefault("X-Request-Id", make_request_id())
        context.update(sid=self.get_cookie("sid"), req_id=self.request.headers.get("X-Request-Id"))

        if not self.auth_required or self.request.method not in self.auth_methods:
            return

        if not self.get_cookie("token"):
            self.finish_noauth()
            return

        token = jwt.decode(self.get_cookie("token", ""))
        if not token.get("id"):
            self.finish_noauth()
            return

    def finish(
        self, chunk: Optional[Union[str, bytes, dict]] = None, status=None, reason=None
    ) -> Future[None]:
        if status:
            self.set_status(status, reason=reason)
        elif chunk is None and not self._status_code:
            self.set_status(204)
        if isinstance(chunk, (dict, list)):
            self.set_header('content-type', 'application/json')# noqa: E702
        return super().finish(chunk)

    def finish_noauth(self):
        self.finish({"error": "auth required"}, status=403)

    def finish_badrequest(self, message):
        self.finish({"error": message}, status=400)

    def finish_internalerror(self, message):
        self.finish({"error": message}, status=500)

    def data_received(self, chunk):
        pass

    @lru_cache()
    def _decode_token(self, token) -> dict:
        if not token:
            return {}
        secret_key = "your-secret-key"
        return jwt.decode(token, key=secret_key, algorithms=["HS256"])

    def get_token(self) -> dict:
        return self._decode_token(self.get_cookie("token", ""))

    def write(self, chunk: Union[str, bytes, dict]) -> None:
        if isinstance(chunk, (dict, list)):
            return super().write(json.dumps(chunk, default=self._serialize))
        return super().write(chunk)

    def _serialize(self, obj: object) -> dict:
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)  # type: ignore
        return obj.__dict__

    def get_body(self) -> dict:
        return json.loads(self.request.body.decode())

    def validate_json_body(self, schema: dict) -> Union[dict, None]:
        body = self.get_body()
        try:
            jsonschema.validate(self.get_body(), schema)
            return body
        except jsonschema.ValidationError as e:
            self.finish_badrequest(f"invalid body: {str(e)}")
            return None

    async def send_event(self, event_name, level=None, detail=None, item=None):
        await sse.SSE_SERVICE.get_channel(self.get_cookie("sid", "")).send_event(
            event_name, level=level, detail=detail, item=item
        )

    async def run_on_executor(self, fn):
        return await tornado.ioloop.IOLoop.current().run_in_executor(self.executor, fn)

    # def write_error(self, status_code, **kwargs):
    #     self.set_header('Content-Type', 'application/json')
    #     if 'exc_info' in kwargs:
    #         logger.exception("unexcept error")

    #         error = traceback.format_exception_only(*kwargs["exc_info"][:-1])[0]
    #         self.finish_internalerror(error.strip())
    #     else:
    #         super().write_error(status_code, **kwargs)
