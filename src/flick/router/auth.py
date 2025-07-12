import uuid

import jwt
from loguru import logger

# from loguru import logger
from flick.router import basehandler

secret_key = "your-secret-key"


class Login(basehandler.BaseRequestHandler):

    def get(self):
        token_id = self.get_token_id()
        logger.debug("========= token id: {}", token_id)
        if not token_id:
            self.finish_noauth()
            return
        self.finish({'session_id': token_id})

    def post(self):
        payload = {
            "id": str(uuid.uuid4()),
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        logger.debug("========= token id: {}", payload.get("id"))
        self.set_cookie('token', token)
        self.finish({'session_id': payload.get('id', '')})
