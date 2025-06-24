import argparse
import logging
import os
import subprocess
import sys
from urllib import parse

import flask
import webview  # pylint: disable=import-error
from flask_cors import CORS
from loguru import logger

from flick.common import logging
from flick.core import container, pip

webdir = os.path.join(os.path.dirname(os.getcwd()), "flick-view", "dist")


app = flask.Flask(
    __name__,
    static_folder=os.path.join(webdir, "assets"),
    template_folder=webdir,
    static_url_path="/assets",
)
CORS(app)


@app.route("/")
def index():
    index_html = os.path.join(webdir, "index.html")
    if os.path.exists(index_html):
        return flask.render_template("index.html")
    return {"error": "Index HTML file not found"}, 404


@app.route("/pip/version")
def get_pip_version():
    return flask.jsonify({"version": pip.SERVICE.version()})


@app.route("/pip/packages")
def list_packages():
    name = flask.request.args.get("name")
    return flask.jsonify({"packages": pip.SERVICE.list_packages(name=name)})


@app.route("/pip/packages/<name>", methods=["DELETE"])
def uninstall_package(name):
    try:
        pip.SERVICE.uninstall(name)
        return {}
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to uninstall package {name}: {e}")
        return flask.jsonify({"error": str(e)}), 500


@app.route("/pip/packages", methods=["POST"])
def install_package():
    if not flask.request.json:
        return flask.jsonify({"success": False, "error": "body is required"}), 400
    name = flask.request.json.get("name")
    no_deps = flask.request.json.get("noDeps", False)
    upgrade = flask.request.json.get("upgrade", False)
    force = flask.request.json.get("force", False)
    if not name:
        return flask.jsonify({"success": False, "error": "name is required"}), 400
    try:
        pip.SERVICE.install(name, upgrade=upgrade, no_deps=no_deps, force=force)
        return flask.jsonify({"success": True})
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install package {name}: {e}")
        return flask.jsonify({"success": False, "error": str(e)}), 500


@app.route("/pip/packages/<name>/versions")
def get_package_versions(name):
    try:
        return flask.jsonify({"versions": pip.SERVICE.get_package_versions(name)})
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install package {name}: {e}")
        return flask.jsonify({"error": str(e)}), 500


@app.route("/pip/repos")
def get_repos():
    return flask.jsonify({"repos": pip.PIP_REPOS})


@app.route("/pip/config")
def get_pip_config():
    return flask.jsonify({"config": pip.SERVICE.config_list()})


@app.route("/pip/config", methods=["POST"])
def set_pip_config():
    if not flask.request.json:
        return flask.jsonify({"success": False, "error": "body is required"}), 400

    key = flask.request.json.get("key")
    value = flask.request.json.get("value")
    if not key or not key:
        return (
            flask.jsonify({"success": False, "error": "key and value is required"}),
            400,
        )

    logger.debug("set pip config {} = {}", key, value)
    pip.SERVICE.config_set(key, value)
    if key == "global.index-url":
        result = parse.urlparse(value)
        pip.SERVICE.config_set("global.trusted-host", result.hostname)

    return {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug")
    parser.add_argument("--dev", action="store_true", help="Enable development mode")
    parser.add_argument(
        "-w", "--webview", action="store_true", help="Enable webview mode"
    )

    args = parser.parse_args(sys.argv[1:])

    logging.setup_logger(level="DEBUG" if args.debug else "INFO")

    logger.info(f"template folder: {app.template_folder}")

    if args.webview:
        logger.info("create webview window")
        webview.create_window("Flick", app, http_port=5000, width=1480, height=1000)
        logger.info("start webview")
        webview.start(debug=False)
    else:
        app.run(debug=args.dev)


@app.route("/docker/images")
def get_images():
    return {"images": container.SERVICE.images()}


if __name__ == "__main__":
    main()
