import argparse
import logging
import os
import sys

import flask
from flask_cors import CORS
from flask_restful import Api
from loguru import logger

from flick.common import logging
from flick.router import base, docker, node, pip

web_dir = os.path.join(os.path.dirname(os.getcwd()), "flick-view", "dist")
if not os.path.exists(web_dir):
    web_dir = os.path.join("/", "usr", "share", "flick-view")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug")
    parser.add_argument("--dev", action="store_true", help="Enable development mode")
    parser.add_argument("-w", "--webview", action="store_true", help="Enable webview mode")

    args = parser.parse_args(sys.argv[1:])

    logging.setup_logger(level="DEBUG" if args.debug else "INFO")

    app = flask.Flask(
        __name__,
        static_folder=os.path.join(web_dir, "assets"),
        template_folder=web_dir,
        static_url_path="/assets",
    )
    base.STATIC_PATH = web_dir

    logger.info("template folder: {}", app.template_folder)
    if app.template_folder and not os.path.exists(app.template_folder):
        logger.warning("template folder not exists")

    CORS(app)

    api = Api(app)
    api.add_resource(base.Index, "/")
    api.add_resource(base.Logo, "/favicon.ico")

    api.add_resource(pip.Version, "/pip/version")
    api.add_resource(pip.Packages, "/pip/packages")
    api.add_resource(pip.Package, "/pip/packages/<name>")
    api.add_resource(pip.PackageVersion, "/pip/packages/<name>/versions")
    api.add_resource(pip.Repos, "/pip/repos")
    api.add_resource(pip.Config, "/pip/config")

    api.add_resource(node.Info, "/node/info")
    api.add_resource(node.Cpu, "/node/cpu")
    api.add_resource(node.Memory, "/node/memory")
    api.add_resource(node.Partitions, "/node/partitions")
    api.add_resource(node.NetInterfaces, "/node/net_interfaces")

    api.add_resource(docker.System, "/docker/system")
    api.add_resource(docker.Images, "/docker/images")

    if args.webview:
        from flick.plugin import \
            window  # pylint: disable=import-outside-toplevel

        window.create_and_start_window(app, debug=args.debug)
    else:
        app.run(debug=args.dev)


if __name__ == "__main__":
    main()
