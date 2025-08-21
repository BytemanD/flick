
from loguru import logger

from flick.router import basehandler
from flick.service import webrequest


class Requests(basehandler.BaseRequestHandler):

    async def get(self):
        logger.info("list all web requests")
        requests = webrequest.SERVICE.list_request()
        requests.sort(key=lambda x: x.send_time, reverse=True)
        self.finish({"requests": [request.model_dump() for request in requests]}, status=200)

    async def post(self):
        data = self.get_body()
        method = data.get("method")
        url = data.get("url")
        body = data.get("body", '')
        headers = data.get("headers", {})
        if not method or not url:
            self.finish_badrequest({"success": False, "error": "method or url is required"})
            return

        try:
            request = webrequest.SERVICE.send_request(method, url, body=body, headers=headers)
        except RuntimeError as e:
            self.finish_internalerror({"success": False, "error": str(e)})
            return
        self.finish({"request": request.model_dump()}, status=202)


class Request(basehandler.BaseRequestHandler):

    async def delete(self, req_id):
        logger.info("list all web requests")
        webrequest.SERVICE.delete_request(int(req_id))
        self.finish(status=204)
