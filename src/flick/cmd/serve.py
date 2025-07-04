import logging
import os

import flask
from cleo.commands.command import Command
from cleo.helpers import option
from flask_cors import CORS
from flask_restful import Api
from loguru import logger

from flick.common import logging
from flick.router import auth, base, docker, node, pip, sse


class ServeCommand(Command):
    name = "serve"
    description = "Start flick server"
    options = [
        option("debug", "d", flag=True, description="Enable debug"),
        option("dev", flag=True, description="Enable development mode"),
        option("webview", "w", flag=True, description="Enable webview mode"),
        option("host", flag=False, default="127.0.0.1", description="Host"),
        option("port", flag=False, default=5000, description="Port"),
    ]

    def handle(self):
        logging.setup_logger(level="DEBUG" if self.option("debug") else "INFO")

        web_dir = os.path.join(os.path.dirname(os.getcwd()), "flick-view", "dist")
        if not os.path.exists(web_dir):
            web_dir = os.path.join("/", "usr", "share", "flick-view")
        app = flask.Flask(
            __name__,
            static_folder=os.path.join(web_dir, "assets"),
            template_folder=web_dir,
            static_url_path="/assets",
        )
        app.secret_key = "secret-key"

        base.STATIC_PATH = web_dir

        logger.info("template folder: {}", app.template_folder)
        if app.template_folder and not os.path.exists(app.template_folder):
            logger.warning("template folder not exists")

        CORS(app)

        app.before_request(auth.check_auth)
        # app.after_request(auth.set_cors_header)

        api = Api(app)
        api.add_resource(base.Index, "/")
        api.add_resource(base.Logo, "/favicon.ico")

        api.add_resource(auth.Login, "/auth/login")
        api.add_resource(sse.SSE, "/sse")

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
        api.add_resource(docker.Containers, "/docker/containers")
        api.add_resource(docker.Container, "/docker/containers/<id_or_name>")
        api.add_resource(docker.Volumes, "/docker/volumes")
        api.add_resource(docker.Volume, "/docker/volumes/<name>")

        if self.option("webview"):
            from flick.plugin import \
                window  # pylint: disable=import-outside-toplevel

            window.create_and_start_window(
                app, debug=self.option("debug"), http_port=self.option("host")
            )
        else:
            app.run(debug=self.option("dev"), host=self.option("host"), port=self.option("port"))

        return 0
