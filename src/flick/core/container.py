import dataclasses
from typing import List, Optional

import docker


@dataclasses.dataclass
class Image:
    short_id: str
    tags: List[str]
    size: int
    id: Optional[str] = None


class DockerManager:

    def __init__(self) -> None:
        self.client = docker.from_env()

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
