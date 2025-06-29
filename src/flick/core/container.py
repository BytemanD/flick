import dataclasses
from typing import List, Optional

import docker
import docker.errors
import requests.exceptions
import urllib3.exceptions

from . import exceptions


@dataclasses.dataclass
class Image:
    short_id: str
    tags: List[str]
    size: int
    id: Optional[str] = None

    def __json__(self):
        return dataclasses.asdict(self)

class DockerManager:

    def __init__(self) -> None:
        self._client = None

    @property
    def client(self) -> docker.DockerClient:
        if self._client is None:
            try:
                self._client = docker.from_env()
            except (docker.errors.DockerException,
                    requests.exceptions.ConnectionError,
                    urllib3.exceptions.ProtocolError) as e:
                raise exceptions.CreateDockerClientFailed(str(e))
        return self._client

    def system(self) -> dict:
        info = self.client.info()
        return {
            'version': info['ServerVersion'],
            'root_dir': info['DockerRootDir'],
            'driver': info['Driver'],
            'gpu_supported': bool(info.get('Runtimes', {}).get('nvidia')),
            'containers_running': info['ContainersRunning'],
            'containers_stopped': info['ContainersStopped'],
            'containers_paursed': info['ContainersPaused'],
            'images': info['Images'],
            'containers': info['Containers'],
        }

    def images(self):
        images = self.client.images.list()
        return [
            Image(
                short_id=image.short_id,
                id=image.id,
                tags=image.tags,
                size=image.attrs["Size"],
            )
            for image in images
        ]


SERVICE = DockerManager()
