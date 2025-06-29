import flask
from flask_restful import Resource

STATIC_PATH = ""


class Index(Resource):

    def get(self):
        return flask.send_from_directory(STATIC_PATH, "index.html", mimetype="text/html")


class Logo(Resource):

    def get(self):
        return flask.send_from_directory(
            STATIC_PATH, "favicon.ico", mimetype="image/vnd.microsoft.icon"
        )
