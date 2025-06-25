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
