from loguru import logger

import docker.errors
from urllib import parse

from flick.common import utils
from flick.core import container
from flick.router import basehandler
from flick.service import sse
from flick.router.schemas import docker as docker_schema


class System(basehandler.BaseRequestHandler):

    def get(self):
        self.finish({"system": container.SERVICE.system()})


class Images(basehandler.BaseRequestHandler):

    def get(self):
        show_intermediate = utils.strtobool(self.get_argument("show_intermediate", ""))
        self.finish({"images": container.SERVICE.images(show_intermediate=show_intermediate)})

    def delete(self):
        container.SERVICE.prune_images()
        self.finish()


class Image(basehandler.BaseRequestHandler):

    def delete(self, image_id):
        force = utils.strtobool(self.get_argument("force", default="false"))
        try:
            container.SERVICE.remove_image(image_id, force=force)
        except docker.errors.APIError as e:
            logger.error("delete image {} failed: {}", image_id, e)
            self.finish_internalerror(str(e))

        self.finish()


class ImageTags(basehandler.BaseRequestHandler):

    def post(self, image_id):
        """添加镜像Tag
        """
        image_id = parse.unquote(image_id)
        body = self.validate_json_body(docker_schema.image_action_add_tag)
        if not body:
            return
        new_tag = body.get("tag", "").strip()
        values = new_tag.split(":")
        if len(values) > 2 or not values[0]:
            self.finish_badrequest(f'invalid tag: {new_tag}')
            return

        container.SERVICE.add_image_tag(image_id, values[0], values[1] if len(values) == 2 else "")
        self.finish({"image": container.SERVICE.get_image(image_id)})


class ImageTag(basehandler.BaseRequestHandler):

    def delete(self, image_id, tag):
        """删除镜像Tag
        """
        image = container.SERVICE.get_image(image_id)
        if tag not in image.tags:
            self.finish_badrequest(f"image has no tag '{tag}'")
            return
        container.SERVICE.remove_image(tag)
        if len(image.tags) <= 1:
            self.finish()
        else:
            self.finish({"image": container.SERVICE.get_image(image_id)})


class Containers(basehandler.BaseRequestHandler):

    def get(self):
        all_status = utils.strtobool(self.get_argument("all_status", ""))
        self.finish({"containers": container.SERVICE.containers(all_status=all_status)})


class Container(basehandler.BaseRequestHandler):

    def get(self, id_or_name):
        self.finish({"container": container.SERVICE.get_container(id_or_name)})

    def delete(self, id_or_name):
        container.SERVICE.rm_container(id_or_name)

    def put(self, id_or_name):
        body = self.get_body()
        status = body.get("status")
        if status in ["running", "acitve"]:
            self.finish({"result": "accept"})
            self._start_container_and_wait(self.get_token_id(), id_or_name)
        elif status in ["stop"]:
            self.finish({"result": "accept"})
            self._stop_container_and_wait(self.get_token_id(), id_or_name)
        elif status in ["pause"]:
            container.SERVICE.pause_container(id_or_name)
            self.finish({"result": "accept"})
        elif status in ["unpause"]:
            container.SERVICE.unpause_container(id_or_name)
            self.finish({"result": "accept"})
        else:
            self.finish_badrequest(f"invalid status {status}")

    def _start_container_and_wait(self, session_id, id_or_name: str):
        updated = container.SERVICE.start_container(id_or_name, wait=True)
        sse.SSE_SERVICE.get_channel(session_id).send_event(
            "started container",
            level="success",
            detail=id_or_name,
            item=updated.to_json(),
        )

    def _stop_container_and_wait(self, session_id, id_or_name: str):
        updated = container.SERVICE.stop_container(id_or_name, wait=True)
        sse.SSE_SERVICE.get_channel(session_id).send_event(
            "stopped container",
            level="success",
            detail=id_or_name,
            item=updated.to_json(),
        )


class Volumes(basehandler.BaseRequestHandler):

    def get(self):
        self.finish({"volumes": container.SERVICE.volumes()})

    def post(self):
        body = self.get_body()
        self.finish(
            {
                "volume": container.SERVICE.create_volume(
                    name=body.get("name"), driver=body.get("driver"), label=body.get("label")
                )
            }
        )


class Volume(basehandler.BaseRequestHandler):

    def get(self, name):
        self.finish({"volume": container.SERVICE.get_volume(name)})

    def delete(self, name):
        container.SERVICE.rm_volume(name)
        self.finish()
