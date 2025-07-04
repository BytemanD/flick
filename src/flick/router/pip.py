import subprocess
from urllib import parse

import flask
from flask_restful import Resource
from loguru import logger

from flick.core import pip
from flick.service import sse, task


class Version(Resource):

    def get(self):
        return flask.jsonify({"version": pip.SERVICE.version()})


class Packages(Resource):

    def get(self):
        name = flask.request.args.get("name")
        return flask.jsonify({"packages": pip.SERVICE.list_packages(name=name)})

    def post(self):
        if not flask.request.json:
            return flask.jsonify({"error": "body is required"}), 400
        name = flask.request.json.get("name")
        no_deps = flask.request.json.get("noDeps", False)
        upgrade = flask.request.json.get("upgrade", False)
        force = flask.request.json.get("force", False)
        if not name:
            return flask.jsonify({"success": False, "error": "name is required"}), 400

        task.start_task(self._install_package, name, upgrade=upgrade, no_deps=no_deps, force=force)

    async def _install_package(self, name, upgrade=False, no_deps=False, force=False):
        try:
            package = pip.SERVICE.install(name, upgrade=upgrade, no_deps=no_deps, force=force)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install package {name}: {e}")
            sse.SSE_SERVICE.send_event(
                "install package failed",
                level="error",
                detail=name,
            )
        else:
            sse.SSE_SERVICE.send_event(
                "installed package",
                level="success",
                detail=name,
                item=package.to_json(),
            )


class Package(Resource):

    def delete(self, name):
        try:
            pip.SERVICE.uninstall(name)
            return {}
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to uninstall package {name}: {e}")
            return flask.jsonify({"error": str(e)}), 500


class PackageVersion(Resource):

    def get(self, name):
        try:
            return flask.jsonify({"versions": pip.SERVICE.get_package_versions(name)})
        except subprocess.CalledProcessError as e:
            logger.error("Failed to get package version of {}: {}", name, e)
            return {"error": str(e)}, 500


class Repos(Resource):

    def get(self):
        return flask.jsonify({"repos": pip.PIP_REPOS})


class Config(Resource):

    def get(self):
        return flask.jsonify({"config": pip.SERVICE.config_list()})

    def put(self):
        if not flask.request.json:
            return flask.jsonify({"success": False, "error": "body is required"}), 400

        key = flask.request.json.get("key")
        value = flask.request.json.get("value")
        if not key or not key:
            return flask.jsonify({"error": "key and value is required"}), 400

        logger.debug("set pip config {} = {}", key, value)
        pip.SERVICE.config_set(key, value)
        if key == "global.index-url":
            result = parse.urlparse(value)
            pip.SERVICE.config_set("global.trusted-host", result.hostname)

        return {}
