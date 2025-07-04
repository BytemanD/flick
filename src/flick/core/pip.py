import dataclasses
from importlib import metadata
from typing import List

import requests
from loguru import logger

from flick.common.utils import timed_lru_cache
from flick.core import executor

PIP_REPOS = {
    "官方": "https://pypi.org/simple",
    "清华大学": "https://pypi.tuna.tsinghua.edu.cn/simple",
    "中国科技大学": "https://pypi.mirrors.ustc.edu.cn/simple",
    "阿里云": "https://mirrors.aliyun.com/pypi/simple",
    "腾讯": "http://mirrors.cloud.tencent.com/pypi/simple",
}


@dataclasses.dataclass
class PyPackage:
    name: str
    version: str
    sumary: str = ""
    # metadata: dict = dataclasses.field(default_factory=dict)
    metadata: str = ""

    def __str__(self) -> str:
        return f"<{self.name}:{self.version}>"

    def to_json(self) -> dict:
        return dataclasses.asdict(self)


class PythonManager:

    def __init__(self) -> None:
        self.pip_cmd = executor.Executor("python -m pip")

    def version(self) -> str:
        _, output = self.pip_cmd.execute("--version")
        values = output.strip().split()
        return values[1] if len(values) > 2 else ""

    def last_version(self, name):
        resp = requests.get(f"https://pypi.org/pypi/{name}/json", timeout=60 * 10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("info", {}).get("version")

    def install(self, name, upgrade=False, no_deps=False, force=False) -> PyPackage:
        args = ["install"]
        if upgrade:
            args.append("--upgrade")
        if no_deps:
            args.append("--no-deps")
        if force:
            args.append("--force")
        args.append(name)
        self.pip_cmd.execute(*args)
        return self.get_package(name=name.split("==")[0])

    def uninstall(self, name):
        self.pip_cmd.execute("uninstall", "-y", name)

    def config_list(self) -> str:
        _, stdout = self.pip_cmd.execute("config", "list")
        return stdout

    def config_set(self, key, value):
        self.pip_cmd.execute("config", "set", key, value)

    def _get_metadata(self, dist) -> List[str]:
        return [f"{key.title()}: {value}" for key, value in dist.metadata.items()]

    def get_package(self, name) -> PyPackage:
        logger.info("get package {}", name)
        dist = metadata.distribution(name)
        return PyPackage(
            name=dist.metadata["Name"],
            version=dist.metadata["Version"],
            sumary=dist.metadata["Summary"],
            metadata="\n".join(self._get_metadata(dist)),
        )

    def list_packages(self, name=None) -> List[PyPackage]:
        logger.info("list packages with name={}", name)
        return [
            PyPackage(
                name=dist.metadata["Name"],
                version=dist.metadata["Version"],
                sumary=dist.metadata["Summary"],
                metadata="\n".join(self._get_metadata(dist)),
            )
            for dist in metadata.distributions()
            if (not name or dist.metadata["Name"] == name)
        ]

    @timed_lru_cache(seconds=3600)
    def get_package_versions(self, name) -> List[str]:
        _, stdout = self.pip_cmd.execute("index", "versions", name)
        for line in stdout.split("\n"):
            if line.startswith("Available versions:"):
                return [v.strip() for v in line.split(":")[-1].split(",")]
        return []


SERVICE = PythonManager()
