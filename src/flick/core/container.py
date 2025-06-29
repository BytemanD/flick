import dataclasses
from typing import Dict, List, Optional

import docker
import docker.errors
import requests.exceptions
import urllib3.exceptions

from . import exceptions


@dataclasses.dataclass
class Container:
    short_id: str
    name: str
    status: int
    image: str = ""


@dataclasses.dataclass
class Image:
    short_id: str
    tags: List[str]
    size: int
    id: Optional[str] = None


@dataclasses.dataclass
class Volume:
    short_id: str
    name: str
    mountpoint: str = ""
    driver: str = ""
    created_at: str = ""
    labels: Optional[Dict[str, str]] = None


class DockerManager:

    def __init__(self) -> None:
        self._client = None

    @property
    def client(self) -> docker.DockerClient:
        if self._client is None:
            try:
                self._client = docker.from_env()
            except (
                docker.errors.DockerException,
                requests.exceptions.ConnectionError,
                urllib3.exceptions.ProtocolError,
            ) as e:
                raise exceptions.CreateDockerClientFailed(str(e))
        return self._client

    def system(self) -> dict:
        info = self.client.info()
        return {
            "version": info["ServerVersion"],
            "root_dir": info["DockerRootDir"],
            "driver": info["Driver"],
            "gpu_supported": bool(info.get("Runtimes", {}).get("nvidia")),
            "containers_running": info["ContainersRunning"],
            "containers_stopped": info["ContainersStopped"],
            "containers_paursed": info["ContainersPaused"],
            "images": info["Images"],
            "containers": info["Containers"],
        }

    def containers(self, all_status=False):
        containers = self.client.containers.list(all=all_status)
        return [
            Container(
                short_id=container.short_id,
                name=container.name,
                status=container.status,
            )
            for container in containers
        ]

    def images(self, show_intermediate=False):
        images = self.client.images.list(all=show_intermediate)
        return [
            Image(
                short_id=image.short_id,
                id=image.id,
                tags=image.tags,
                size=image.attrs["Size"],
            )
            for image in images
        ]

    def volumes(self) -> List[Volume]:
        items = self.client.volumes.list()
        return [
            Volume(
                short_id=volume.short_id,
                name=volume.name,
                labels=volume.attrs.get("Labels") or {},
                driver=volume.attrs["Driver"],
                mountpoint=volume.attrs["Mountpoint"],
                created_at=volume.attrs["CreatedAt"],
            )
            for volume in items
        ]

    def rm_volume(self, volume_id, force=False):
        volume = self.client.volumes.get(volume_id)
        volume.remove(force=force)


SERVICE = DockerManager()
