import flask
from flask import jsonify
from flask_restful import Resource

from flick.common import utils
from flick.core import container
from ._argparser import query_parser, ReqArg


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
    query_parser = query_parser([
        ReqArg("all_status", type=utils.strtobool),
    ])  # fmt: skip

    def get(self):
        args = self.query_parser.parse_args(flask.request)
        all_status = args.get("all_status", False)
        return jsonify({"containers": container.SERVICE.containers(all_status=all_status)})


class Volumes(Resource):

    def get(self):
        return jsonify({"volumes": container.SERVICE.volumes()})


class Volume(Resource):

    def options(self, name):
        return {}

    def delete(self, name):
        return container.SERVICE.rm_volume(name)
