import subprocess
from urllib import parse

from loguru import logger
import tornado

from flick.common import utils
from flick.core import pip
from flick.router import basehandler
from flick.service import sse, task


class Version(basehandler.BaseRequestHandler):

    def get(self):
        return self.finish({"version": pip.SERVICE.version()})


class Packages(basehandler.BaseRequestHandler):

    def get(self):
        name = self.get_query_argument("name", None)
        self.finish({"packages": pip.SERVICE.list_packages(name=name)})

    async def post(self):
        data = self.get_body()
        name = data.get("name")
        no_deps = data.get("noDeps", False)
        upgrade = data.get("upgrade", False)
        force = data.get("force", False)
        if not name:
            self.finish_badrequest({"success": False, "error": "name is required"})
            return

        self.finish(status=202)
        try:
            package = await self._install_package(
                name,
                upgrade=upgrade,
                no_deps=no_deps,
                force=force,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install package {name}: {e}")
            await self.send_event(
                "install package failed",
                level="error",
                detail=name,
            )
        else:
            await self.send_event(
                "installed package",
                level="success",
                detail=name,
                item=package.to_json(),
            )

    @tornado.concurrent.run_on_executor
    async def _install_package(self, name, upgrade=False, no_deps=False, force=False):
        return pip.SERVICE.install(name, upgrade=upgrade, no_deps=no_deps, force=force)


class Package(basehandler.BaseRequestHandler):

    async def delete(self, name):
        self.finish({}, status=202)
        # task.submit(self._uninstall_package_and_wait, self.get_token_id(), name)
        try:
            await self._uninstall_package_and_wait(name)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to uninstall package {name}: {e}")
            await self.send_event(
                "update package failed",
                level="error",
                detail=name,
            )
        else:
            await self.send_event(
                "uninstalled package",
                level="success",
                detail=name,
            )

    async def put(self, name):
        data = self.get_body()
        version = data.get("version")
        if version:
            # task.submit(
            #     self._update_package_and_wait,
            #     self.get_token_id(),
            #     name,
            #     version,
            #     no_deps=data.get("noDeps", False),
            #     force=data.get("force", False),
            # )
            try:
                package = await self._update_package_and_wait(
                    name, version, no_deps=data.get("noDeps", False), force=data.get("force", False)
                )
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install package {name}: {e}")
                await self.send_event(
                    "update package failed",
                    level="error",
                    detail=name,
                )
            else:
                logger.info("update package {} -> {} success", name, version)
                await self.send_event(
                    "updated package",
                    level="success",
                    detail=name,
                    item=package.to_json(),
                )
        self.finish({}, status=202)

    @tornado.concurrent.run_on_executor
    def _uninstall_package_and_wait(self, name):
        pip.SERVICE.uninstall(name)

    @tornado.concurrent.run_on_executor
    def _update_package_and_wait(self, name, version, no_deps=False, force=False):
        return pip.SERVICE.upgrade(name, version, no_deps=no_deps, force=force)


class PackageVersion(basehandler.BaseRequestHandler):

    def get(self, name):
        try:
            self.finish({"versions": pip.SERVICE.get_package_versions(name)})
        except subprocess.CalledProcessError as e:
            logger.error("Failed to get package version of {}: {}", name, e)
            self.finish({"error": str(e)}, 500)


class Repos(basehandler.BaseRequestHandler):

    def get(self):
        self.finish({"repos": pip.PIP_REPOS})


class Config(basehandler.BaseRequestHandler):

    def get(self):
        self.finish({"config": pip.SERVICE.config_list()})

    def put(self):
        data = self.get_body()
        if not data:
            self.finish_badrequest("body is required")
            return

        key = data.get("key")
        value = data.get("value")
        if not key or not value:
            self.finish_badrequest("key and value is required")
            return

        logger.debug("set pip config {} = {}", key, value)
        pip.SERVICE.config_set(key, value)
        if key == "global.index-url":
            result = parse.urlparse(value)
            pip.SERVICE.config_set("global.trusted-host", result.hostname)

        self.finish()
