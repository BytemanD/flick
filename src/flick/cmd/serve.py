import logging
import os

from cleo.commands.command import Command
from cleo.helpers import option
from loguru import logger
from tornado import web
from tornado import httpserver
from tornado import ioloop
from tornado import autoreload

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

        web_dirs = [
            os.path.join(os.path.dirname(os.getcwd()), "flick-view", "dist"),
            os.path.join(os.path.dirname("flick-view")),
            os.path.join("/", "usr", "share", "flick-view"),
        ]
        web_dir = ""
        for find_dir in web_dirs:
            logger.debug("find template folder: {}", find_dir)
            if os.path.exists(find_dir):
                web_dir = find_dir
                break
        logger.info("template folder: {}", web_dir)
        if web_dir and not os.path.exists(web_dir):
            logger.warning("template folder not exists")
        base.STATIC_PATH = web_dir

        handlers = [
            # (r"/", web.RedirectHandler, {'url': '/index.html'}),
            (r"/", base.Index),
            (r"/index.html", base.Index),
            (r"/favicon.ico", web.StaticFileHandler, {"path": web_dir}),
            (r"/auth/login", auth.Login),
            (r"/sse", sse.SSE),

            (r"/node/info", node.Info),
            (r"/node/cpu", node.Cpu),
            (r"/node/memory", node.Memory),
            (r"/node/partitions", node.Partitions),
            (r"/node/net_interfaces", node.NetInterfaces),

            (r"/pip/version", pip.Version),
            (r"/pip/packages", pip.Packages),
            (r"/pip/packages/([^/]+)/versions", pip.PackageVersion),
            (r"/pip/packages/([^/]+)", pip.Package),
            (r"/pip/repos", pip.Repos),
            (r"/pip/config", pip.Config),

            (r"/docker/system", docker.System),
            (r"/docker/images", docker.Images),
            (r"/docker/images/([^/]+)", docker.Image),
            (r"/docker/images/([^/]+)/tags/(.+)", docker.ImageTag),
            (r"/docker/images/([^/]+)/tags", docker.ImageTags),
            (r"/docker/containers", docker.Containers),
            (r"/docker/containers/([^/]+)", docker.Container),
            (r"/docker/volumes", docker.Volumes),
            (r"/docker/volumes/([^/]+)", docker.Volume),

            (r"/assets/(.*)", web.StaticFileHandler, {"path": os.path.join(web_dir, 'assets')}),
        ]
        app = web.Application(
            handlers,
            template_path=web_dir,
            static_path=web_dir,
            # static_url_prefix="/assets/",
            debug=self.option("debug"),
            compress_response=False,
        )
        http_server = httpserver.HTTPServer(app)
        http_server.listen(self.option("port"))
        logger.info('starting server at {}', self.option("port"))
        if self.option('dev'):
            autoreload.start()
        ioloop.IOLoop.current().start()

        # app = flask.Flask(
        #     __name__,
        #     static_folder=os.path.join(web_dir, "assets"),
        #     template_folder=web_dir,
        #     static_url_path="/assets",
        # )
        # app.secret_key = "secret-key"
        # CORS(app)

        # app.before_request(auth.check_auth)
        # # app.after_request(auth.set_cors_header)

        # api = Api(app)
        # api.add_resource(base.Index, "/")
        # api.add_resource(base.Logo, "/favicon.ico")

        # api.add_resource(auth.Login, "/auth/login")
        # api.add_resource(sse.SSE, "/sse")

        # api.add_resource(pip.Version, "/pip/version")
        # api.add_resource(pip.Packages, "/pip/packages")
        # api.add_resource(pip.Package, "/pip/packages/<name>")
        # api.add_resource(pip.PackageVersion, "/pip/packages/<name>/versions")
        # api.add_resource(pip.Repos, "/pip/repos")
        # api.add_resource(pip.Config, "/pip/config")

        # api.add_resource(node.Info, "/node/info")
        # api.add_resource(node.Cpu, "/node/cpu")
        # api.add_resource(node.Memory, "/node/memory")
        # api.add_resource(node.Partitions, "/node/partitions")
        # api.add_resource(node.NetInterfaces, "/node/net_interfaces")

        # api.add_resource(docker.System, "/docker/system")
        # api.add_resource(docker.Images, "/docker/images")
        # api.add_resource(docker.Image, "/docker/images/<image_id>")
        # api.add_resource(docker.ImageAactions, "/docker/images/actions")
        # api.add_resource(docker.Containers, "/docker/containers")
        # api.add_resource(docker.Container, "/docker/containers/<id_or_name>")
        # api.add_resource(docker.Volumes, "/docker/volumes")
        # api.add_resource(docker.Volume, "/docker/volumes/<name>")

        # if self.option("webview"):
        #     from flick.plugin import window  # pylint: disable=import-outside-toplevel

        #     window.create_and_start_window(
        #         app, debug=self.option("debug"), http_port=self.option("host")
        #     )
        # else:
        #     app.run(debug=self.option("dev"), host=self.option("host"), port=self.option("port"))

        return 0
