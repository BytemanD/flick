import flask
from flask import jsonify
from flask_restful import Resource, abort

from flick.common import utils
from flick.core import container

from ._argparser import ReqArg, query_parser


class System(Resource):

    def get(self):
        return {"system": container.SERVICE.system()}


class Images(Resource):

    def get(self):
        show_intermediate = flask.request.args.get(
            "show_intermediate", default=False, type=utils.strtobool
        )
        return jsonify({"images": container.SERVICE.images(show_intermediate=show_intermediate)})

    def delete(self):
        container.SERVICE.prune_images()
        return {}, 204


class Containers(Resource):
    query_parser = query_parser([
        ReqArg("all_status", type=utils.strtobool),
    ])  # fmt: skip

    def get(self):
        args = self.query_parser.parse_args(flask.request)
        all_status = args.get("all_status", False)
        return jsonify({"containers": container.SERVICE.containers(all_status=all_status)})


class Container(Resource):
    query_parser = query_parser([
        ReqArg("all_status", type=utils.strtobool),
    ])  # fmt: skip

    def options(self, id_or_name):
        return {}

    def get(self, id_or_name):
        return jsonify({"container": container.SERVICE.get_container(id_or_name)})

    def delete(self, id_or_name):
        container.SERVICE.rm_container(id_or_name)

    def put(self, id_or_name):
        body = flask.request.get_json()
        status = body.get("status")
        if status in ["running", "acitve"]:
            container.SERVICE.start_container(id_or_name)
        elif status in ["stop"]:
            container.SERVICE.stop_container(id_or_name)
        elif status in ["pause"]:
            container.SERVICE.pause_container(id_or_name)
        elif status in ["unpause"]:
            container.SERVICE.unpause_container(id_or_name)
        else:
            abort(400, description=f"invalid status {status}")
        return {}


class Volumes(Resource):

    def get(self):
        return jsonify({"volumes": container.SERVICE.volumes()})

    def post(self):
        body = flask.request.get_json()
        body.get("name")
        return container.SERVICE.create_volume(
            name=body.get("name"), driver=body.get("driver"), label=body.get("label")
        )


class Volume(Resource):

    def options(self, name):
        return {}

    def get(self, name):
        return jsonify({"volume": container.SERVICE.get_volume(name)})

    def delete(self, name):
        return container.SERVICE.rm_volume(name)
