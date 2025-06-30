import dataclasses
from typing import Dict, List, Optional

import docker
import docker.errors
import requests.exceptions
import urllib3.exceptions
from docker.models import containers as docker_containers
from docker.models import images as docker_images
from docker.models import volumes as docker_volumes

from . import exceptions


@dataclasses.dataclass
class Container:
    short_id: str
    name: str
    status: str
    image: str = ""

    @classmethod
    def from_raw_object(cls, container: docker_containers.Container):
        return Container(
            short_id=container.short_id,
            name=container.name or "",
            status=container.status or "",
            image=container.attrs["Config"]["Image"],
        )


@dataclasses.dataclass
class Image:
    short_id: str
    tags: List[str]
    size: int
    id: Optional[str] = None

    @classmethod
    def from_raw_object(cls, image: docker_images.Image):
        return Image(
            short_id=image.short_id,
            id=image.id,
            tags=image.tags,
            size=image.attrs["Size"],
        )


@dataclasses.dataclass
class Volume:
    short_id: str
    name: str
    mountpoint: str = ""
    driver: str = ""
    created_at: str = ""
    labels: Optional[Dict[str, str]] = None

    @classmethod
    def from_raw_object(cls, volume: docker_volumes.Volume):
        return Volume(
            short_id=volume.short_id,
            name=volume.name,
            labels=volume.attrs.get("Labels") or {},
            driver=volume.attrs["Driver"],
            mountpoint=volume.attrs["Mountpoint"],
            created_at=volume.attrs["CreatedAt"],
        )


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
        return [Container.from_raw_object(container) for container in containers]

    def _get_container(self, id_or_name: str) -> docker_containers.Container:
        container = self.client.containers.get(id_or_name)
        if not container:
            raise exceptions.ContainerNotExists(id_or_name)
        return container

    def get_container(self, id_or_name: str):
        return Container.from_raw_object(self._get_container(id_or_name))

    def rm_container(self, id_or_name: str, force=False):
        container = self._get_container(id_or_name)
        container.remove(force=force)

    def start_container(self, id_or_name: str):
        container = self._get_container(id_or_name)
        container.start()

    def stop_container(self, id_or_name: str, timeout=None):
        container = self._get_container(id_or_name)
        container.stop(timeout=timeout)

    def pause_container(self, id_or_name: str):
        container = self._get_container(id_or_name)
        container.pause()

    def unpause_container(self, id_or_name: str):
        container = self._get_container(id_or_name)
        container.unpause()

    def resize_container(self, id_or_name: str, height: int, width: int):
        container = self._get_container(id_or_name)
        container.resize(height, width)

    def images(self, show_intermediate=False):
        images = self.client.images.list(all=show_intermediate)
        return [Image.from_raw_object(image) for image in images]

    def prune_images(self):
        self.client.images.prune()

    def volumes(self) -> List[Volume]:
        items = self.client.volumes.list()
        return [Volume.from_raw_object(volume) for volume in items]

    def get_volume(self, volume_id) -> Volume:
        volume = self.client.volumes.get(volume_id)
        return Volume.from_raw_object(volume)

    def create_volume(
        self, name=None, driver=None, label: Optional[dict[str, str]] = None
    ) -> Volume:
        volume = self.client.volumes.create(name=name, driver=driver, label=label)
        return Volume.from_raw_object(volume)

    def rm_volume(self, volume_id, force=False):
        volume = self.client.volumes.get(volume_id)
        volume.remove(force=force)


SERVICE = DockerManager()
