from flask import jsonify
from flask_restful import Resource

from flick.core import container


class System(Resource):

    def get(self):
        return {'system': container.SERVICE.system()}


class Images(Resource):

    def get(self):
        # import pdb; pdb.set_trace()
        return jsonify({"images": container.SERVICE.images()})
