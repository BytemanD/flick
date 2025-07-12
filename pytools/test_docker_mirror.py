import sys
from typing import Set
from urllib import parse
from concurrent.futures import ThreadPoolExecutor

import docker
import docker.errors
import prettytable
from loguru import logger


MIRRORS = """
https://docker-0.unsee.tech
https://docker.m.daocloud.io
https://docker.hlmirror.com
https://docker-mirror.aigc2d.com
https://dockertest.jsdelivr.fyi
https://docker.ameke.cn
https://docker.m.daocloud.io
https://docker.1ms.run
# https://registry.cyou
# https://dockerpull.pw
# https://docker.hpcloud.cloud
# https://docker.imgdb.de
# https://docker.1panel.top
# https://docker.aeko.cn
# https://docker.unsee.tech
# https://docker.1panel.live
# https://docker.xuanyuan.me
# https://demo.52013120.xyz
# https://docker.chenby.cn
# http://mirror.azure.cn
# https://dockerpull.org
# https://dockerhub.icu
# https://hub.rat.dev
# https://proxy.1panel.live
# http://mirrors.ustc.edu.cn
# https://docker.ketches.cn
"""

docker_client = docker.from_env()


class PullResult:

    def __init__(self, image, success, message=None) -> None:
        self.image = image
        self.success = success
        self.message = message


def docker_image_exists(images: Set[str]) -> bool:
    for image in images:
        try:
            docker_client.images.get(image)
        except docker.errors.ImageNotFound:
            continue
        logger.info("found image {}", image)
        return True

    return False


def docker_pull(image: str):
    logger.info("pull image: {}", image)
    values = image.split(":")
    repository = values[0]
    tag = values[1] if len(values) > 1 else None
    try:
        docker_client.images.pull(repository, tag=tag)
    except docker.errors.APIError as e:
        return PullResult(image, False, message=str(e))
    else:
        return PullResult(image, True, message="")


def docker_pull_from_any_mirror(image: str):
    pull_images = set([])
    for line in MIRRORS.split("\n"):
        if not line or line.strip().startswith("#"):
            continue
        url = parse.urlparse(line)
        if url.scheme:
            pull_images.add(f"{url.hostname}/{image}")
        else:
            pull_images.add(f"{line.strip()}/{image}")

    if docker_image_exists(pull_images):
        logger.warning("image {} exists", image)
        return

    logger.info("try to pull image: {}", image)

    table = prettytable.PrettyTable(["#", "image", "result", "message"])
    table.max_width.update({"message": 100})
    table.align.update({"image": "l", "result": "l", "message": "l"})
    table.sortby = "result"
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(docker_pull, i) for i in pull_images]
        if not futures:
            return
        for index, future in enumerate(futures, start=1):
            result = future.result()
            table.add_row(
                [
                    f"{index:0>2}",
                    result.image,
                    result.success and "success" or "xxxxxxx",
                    result.message or "",
                ]
            )
            if result.success:
                logger.success("pull success: {}", result.image)
                break
            if not result.success:
                logger.error("pull failed: {}", result.image)

        for future in futures:
            future.cancel()
    print(table)


def main():
    image = sys.argv[1]
    for image in sys.argv[1:]:
        docker_pull_from_any_mirror(image)


if __name__ == "__main__":
    main()
