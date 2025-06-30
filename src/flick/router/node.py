import flask
from flask_restful import Resource

from flick.common import utils
from flick.core import node

from ._argparser import ReqArg, query_parser


class Info(Resource):

    def get(self):
        return {"info": node.SERVICE.platform()}


class Cpu(Resource):

    def get(self):
        return {"cpu": node.SERVICE.cpu()}


class Memory(Resource):

    def get(self):
        return {"memory": node.SERVICE.memory()}


class Partitions(Resource):
    query_parser = query_parser([
        ReqArg("all_device", type=utils.strtobool),
    ])  # fmt: skip

    def get(self):
        args = self.query_parser.parse_args(flask.request)
        all_device = args.get("all_device", False)
        return flask.jsonify({"partitions": node.SERVICE.partitions(all_device=all_device)})


class NetInterfaces(Resource):

    def get(self):
        return flask.jsonify({"net_interfaces": node.SERVICE.net_interfaces()})
