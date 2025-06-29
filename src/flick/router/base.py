import os

import flask
from flask_restful import Resource

STATIC_PATH = ""


class Index(Resource):

    def get(self):
        index_html = os.path.join(STATIC_PATH, "index.html")
        if os.path.exists(index_html):
            return flask.render_template("index.html")
        return {"error": "Index HTML file not found"}, 404


class Logo(Resource):

    def get(self):
        return flask.send_from_directory(
            STATIC_PATH, "favicon.ico", mimetype="image/vnd.microsoft.icon"
        )
