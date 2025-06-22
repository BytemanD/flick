from typing import List
import dataclasses
from importlib import metadata

from loguru import logger
import requests

from flick.common.utils import timed_lru_cache
from flick.core import executor


@dataclasses.dataclass
class PyPackage:
    name: str
    version: str
    sumary: str = ''
    # metadata: dict = dataclasses.field(default_factory=dict)
    metadata: str = ""

    def __str__(self) -> str:
        return f'<{self.name}:{self.version}>'


class PythonManager:

    def __init__(self) -> None:
        self.pip_cmd = executor.Executor('python -m pip')

    def version(self) -> str:
        _, output = self.pip_cmd.execute('--version')
        values = output.strip().split()
        return values[1] if len(values) > 2 else ''

    def last_version(self, name):
        resp = requests.get(f'https://pypi.org/pypi/{name}/json')
        resp.raise_for_status()
        data = resp.json()
        return data.get('info', {}).get('version')

    def install(self, name, upgrade=False, no_deps=False, force=False):
        args = ['install']
        if upgrade:
            args.append('--upgrade')
        if no_deps:
            args.append('--no-deps')
        if force:
            args.append('--force')
        args.append(name)
        self.pip_cmd.execute(*args)

    def uninstall(self, name):
        self.pip_cmd.execute('uninstall', '-y', name)

    def config_list(self) -> str:
        _, stdout = self.pip_cmd.execute('config', 'list')
        return stdout

    def config_set(self, key, value):
        self.pip_cmd.execute('config', 'set', key, value)

    def list_packages(self, name=None) -> List[PyPackage]:
        logger.info('list packages with name={}', name)
        return [
            PyPackage(name=dist.metadata['Name'], version=dist.metadata['Version'],
                      sumary=dist.metadata['Summary'],
                      metadata=dist.metadata.as_string())
            for dist in metadata.distributions() if (not name or dist.metadata['Name'] == name)
        ]

    @timed_lru_cache(seconds=3600)
    def get_package_versions(self, name) -> List[str]:
        _, stdout = self.pip_cmd.execute('index', 'versions', name)
        for line in stdout.split('\n'):
            if line.startswith("Available versions:"):
                return [v.strip() for v in line.split(':')[-1].split(',')]
        return []


SERVICE = PythonManager()
