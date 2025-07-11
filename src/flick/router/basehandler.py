from functools import lru_cache
import dataclasses
import json
from typing import List, Optional, Union
from tornado import gen

import jwt
from tornado import web
import jsonschema
from tornado.concurrent import Future


class BaseRequestHandler(web.RequestHandler):
    auth_required = False
    auth_methods = ["GET", "POST", "PUT", "DELETE"]

    def prepare(self):
        super().prepare()
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
        elif chunk is None:
            self.set_status(204)
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
    def _get_token(self, token) -> dict:
        if not token:
            return {}
        secret_key = "your-secret-key"
        return jwt.decode(token,  key=secret_key, algorithms=["HS256"])

    def get_token_id(self) -> str:
        token = self._get_token(self.get_cookie("token", ""))
        return token.get("id", "")

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
            self.finish_badrequest(f'invalid body: {str(e)}')
            return None
