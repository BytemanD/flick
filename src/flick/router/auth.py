import uuid

import flask
from flask_restful import Resource

# from loguru import logger


class Login(Resource):

    def options(self):
        return {}

    def post(self):
        # TODO
        flask.session["id"] = str(uuid.uuid4())
        flask.session["username"] = "guest"
        return flask.jsonify({"session_id": flask.session["id"]})


def check_auth():
    if flask.request.path == "/auth/login" and flask.request.method in ["POST", "OPTIONS"]:
        return
    if flask.request.method == "GET" and flask.request.path == "/sse":
        return
    if "username" not in flask.session or "id" not in flask.session:
        return {"error": "no auth"}, 403

