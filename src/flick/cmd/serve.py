import os
import pathlib
import platform
import sys

from cleo.commands.command import Command
from cleo.helpers import option
from loguru import logger
from tornado import autoreload, httpserver, ioloop, web

from flick.common import log
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
        log.setup_logger(level="DEBUG" if self.option("debug") else "INFO")
        if self.option("debug"):
            log.monkey_patch_logging()

        if hasattr(sys, "_MEIPASS"):
            # 打包后的运行环境
            web_dirs = [pathlib.Path(getattr(sys, "_MEIPASS"), 'flick-view')]
        else:
            web_dirs = [
                # os.path.join(os.path.dirname(os.getcwd()), "flick-view", "dist"),
                # os.path.join(os.path.abspath(os.getcwd()), "flick-view"),
                # os.path.join("/", "usr", "share", "flick-view"),
                pathlib.Path(os.getcwd()) / "flick-view",
                pathlib.Path(os.getcwd()).parent / "flick-view" / "dist",
            ]
            if platform.system().lower() == "linux":
                web_dirs.append(
                    pathlib.Path("/", "usr", "share", "flick-view"),
                )
            elif platform.system().lower() == "windows":
                app_data = os.getenv("PROGRAMDATA") or os.getenv("APPDATA")
                if app_data:
                    web_dirs.append(pathlib.Path(app_data, "flick-view"))

        logger.debug(
            "find web directories on these paths:\n{}", "\n".join([p.as_posix() for p in web_dirs])
        )
        web_dir = ""
        for find_dir in web_dirs:
            logger.debug("find template folder: {}", find_dir)
            if os.path.exists(find_dir):
                web_dir = find_dir
                break
        if web_dir:
            logger.success("found template folder: {}", web_dir)
        else:
            logger.warning("template folder not found")
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
            (r"/assets/(.*)", web.StaticFileHandler, {"path": os.path.join(web_dir, "assets")}),
        ]
        app = web.Application(
            handlers,
            template_path=web_dir,
            static_path=web_dir,
            debug=self.option("debug"),
            compress_response=False,
            cookie_secret="YOUR_SECURE_KEY",
        )
        http_server = httpserver.HTTPServer(app)
        http_server.listen(self.option("port"))
        logger.info("starting server at {}", self.option("port"))
        if self.option("dev"):
            autoreload.start()
        ioloop.IOLoop.current().start()

        # if self.option("webview"):
        #     from flick.plugin import window  # pylint: disable=import-outside-toplevel

        #     window.create_and_start_window(
        #         app, debug=self.option("debug"), http_port=self.option("host")
        #     )
        # else:
        #     app.run(debug=self.option("dev"), host=self.option("host"), port=self.option("port"))

        return 0
