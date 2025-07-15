
import jwt
from loguru import logger

# from loguru import logger
from flick.router import basehandler

secret_key = "your-secret-key"


class Login(basehandler.BaseRequestHandler):

    def get(self):
        token = self.get_token()
        logger.debug("========= token: {}", token)
        if not token:
            self.finish_noauth()
            return
        self.finish(token)

    def post(self):
        payload = {
            "username": 'guest',
        }
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        self.set_cookie('token', token)
        self.flush()
        self.finish({})
