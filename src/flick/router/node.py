import flask
from flask_restful import Resource

from flick.common import utils
from flick.core import node


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

    def get(self):
        all_device = flask.request.args.get("all_device", default=False, type=utils.strtobool)
        return flask.jsonify({"partitions": node.SERVICE.partitions(all_device=all_device)})


class NetInterfaces(Resource):

    def get(self):
        return flask.jsonify({"net_interfaces": node.SERVICE.net_interfaces()})
