import uuid

import flask
from flask_restful import Resource

# from loguru import logger


class Login(Resource):

    def options(self):
        return {}

    def post(self):
        flask.session["id"] = str(uuid.uuid4())
        flask.session["username"] = "guest"
        return flask.jsonify({"session_id": flask.session["id"]})


IGNORE_PATHS = {
    "/auth/login": ["POST", "OPTIONS"],
    "/sse": ["GET"],
    "/index.html": ["GET"],
    "/": ["GET"],
}


def check_auth():
    if flask.request.path.startswith('/assets'):
        return
    if flask.request.path in IGNORE_PATHS and flask.request.method in IGNORE_PATHS.get(
        flask.request.path
    ):
        return
    if "username" not in flask.session or "id" not in flask.session:
        return {"error": "no auth"}, 403
