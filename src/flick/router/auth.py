import json
import uuid

from tornado import web
import jwt

# from loguru import logger
from flick.router import basehandler

secret_key = "your-secret-key"


class Login(basehandler.BaseRequestHandler):

    def post(self):
        payload = {
            "id": str(uuid.uuid4()),
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")

        self.set_cookie('token', token)
        self.finish({'session_id': payload.get('id', '')})
