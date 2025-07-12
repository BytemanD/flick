import asyncio
import json
import time
import uuid
from concurrent import futures
from loguru import logger
import tornado


queues = asyncio.Queue()


class SSEHandler(tornado.web.RequestHandler):

    async def get(self):    
        self.set_header("Content-Type", "text/event-stream")
        self.set_header("Cache-Control", "no-cache")
        self.set_header("Connection", "keep-alive")

        await queues.put('sse connected')
        while True:
            message = await queues.get()
            logger.info("send event data: {}", message)
            try:
                if self._finished:
                    logger.error('sse connection closed')
                    break
                self.write(f"data: {message}\n\n")
                self.flush()
            except Exception as e:
                logger.error('write failed: {}', e)

    def on_connection_close(self):
        self.finish()
        super().on_connection_close()


class EventHander(tornado.web.RequestHandler):

    async def post(self):
        data = self.request.body.decode()
        logger.info("receive event data: {}", data)
        await queues.put(data)
        self.set_status(202)
        self.finish("success\n")


class TaskHander(tornado.web.RequestHandler):
    executor = futures.ThreadPoolExecutor()

    async def post(self):
        self.set_status(202)
        self.finish("success\n")

        result = await self.task1()
        await queues.put(json.dumps(result))

    @tornado.concurrent.run_on_executor
    def task1(self):
        task_id = str(uuid.uuid4())
        logger.info("task {} start", task_id)
        for _ in range(5):
            time.sleep(1)
        logger.info("task {} finish", task_id)
        return {"result": "success", "task_id": task_id}


def main():
    handlers = [
        (r"/sse", SSEHandler),
        (r"/events", EventHander),
        (r"/tasks", TaskHander),
    ]
    app = tornado.web.Application(
        handlers,
        debug=True,
        compress_response=False,
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(5000)
    tornado.autoreload.start()
    logger.info("start server")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
