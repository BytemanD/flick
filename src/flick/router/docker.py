import flask
from flask import jsonify
from flask_restful import Resource

from flick.common import utils
from flick.core import container


class System(Resource):

    def get(self):
        return {"system": container.SERVICE.system()}


class Images(Resource):

    def get(self):
        show_intermediate = flask.request.args.get(
            "show_intermediate", default=False, type=utils.strtobool
        )
        return jsonify({"images": container.SERVICE.images(show_intermediate=show_intermediate)})


class Containers(Resource):

    def get(self):
        all_status = flask.request.args.get("all_status", default=False, type=utils.strtobool)
        return jsonify({"containers": container.SERVICE.containers(all_status=all_status)})


class Volumes(Resource):

    def get(self):
        return jsonify({"volumes": container.SERVICE.volumes()})

class Volume(Resource):

    def options(self, name):
        return {}

    def delete(self, name):
        return container.SERVICE.rm_volume(name)
