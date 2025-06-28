import argparse
import logging
import os
import subprocess
import sys
from urllib import parse

import flask
from flask_cors import CORS
from loguru import logger

from flick.common import logging
from flick.common import utils
from flick.core import container, node, pip

web_dir = os.path.join(os.path.dirname(os.getcwd()), "flick-view", "dist")
if not os.path.exists(web_dir):
    web_dir = os.path.join("/", "usr", "share", "flick-view")

app = flask.Flask(
    __name__,
    static_folder=os.path.join(web_dir, "assets"),
    template_folder=web_dir,
    static_url_path="/assets",
)
CORS(app)


@app.route("/")
def index():
    index_html = os.path.join(web_dir, "index.html")
    if os.path.exists(index_html):
        return flask.render_template("index.html")
    return {"error": "Index HTML file not found"}, 404


@app.route("/favicon.ico")
def favicon_ico():
    return flask.send_from_directory(web_dir, "favicon.ico", mimetype="image/vnd.microsoft.icon")


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


@app.route("/docker/images")
def get_images():
    try:
        return {"images": container.SERVICE.images()}
    except Exception as e:
        logger.error("interval server error: {}", str(e))
        return {}, 500


@app.route("/node/info")
def get_system_info():
    return {"info": node.SERVICE.platform()}


@app.route("/node/cpu")
def get_node_cpu():
    return {"cpu": node.SERVICE.cpu()}


@app.route("/node/memory")
def get_node_memory():
    return {"memory": node.SERVICE.memory()}


@app.route("/node/partitions")
def get_node_disk():
    all_device = flask.request.args.get('all_device', default=False,
                                        type=utils.strtobool)
    return {"partitions": node.SERVICE.partitions(all_device=all_device)}


@app.route("/node/net_interfaces")
def get_node_net_interfaces():
    return {"net_interfaces": node.SERVICE.net_interfaces()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug")
    parser.add_argument("--dev", action="store_true", help="Enable development mode")
    parser.add_argument("-w", "--webview", action="store_true", help="Enable webview mode")

    args = parser.parse_args(sys.argv[1:])

    logging.setup_logger(level="DEBUG" if args.debug else "INFO")

    logger.info("template folder: {}", app.template_folder)
    if app.template_folder and not os.path.exists(app.template_folder):
        logger.warning("template folder not exists")

    if args.webview:
        from flick.plugin import window  # pylint: disable=import-outside-toplevel

        window.create_and_start_window(app, debug=args.debug)
    else:
        app.run(debug=args.dev)


if __name__ == "__main__":
    main()
