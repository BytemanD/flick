import contextlib
import os
import pathlib
from datetime import datetime
from typing import List, Optional

from loguru import logger
import pydantic
import requests
import tinydb
from tinydb.table import Document

from flick.common import utils


class Response(pydantic.BaseModel):
    elapsed: float
    status_code: int
    reason: str
    headers: Optional[dict] = None
    body: Optional[str] = None


class Request(pydantic.BaseModel):
    id: int
    send_time: str
    method: str
    url: str
    headers: Optional[dict] = None
    body: Optional[str] = None

    response: Optional[Response] = None

    @classmethod
    def from_document(cls, doc: Document) -> "Request":
        return cls(
            id=doc.doc_id,
            send_time=doc.get("send_time", 0.0),
            method=doc.get("method", ""),
            url=doc.get("url", ""),
            headers=doc.get("headers", {}),
            body=doc.get("body"),
            response=Response(**doc.get("response", {})) if doc.get("response") else None,
        )


class TinyDbImpl:

    def __init__(self, db_path: Optional[pathlib.Path] = None) -> None:
        self.db_file = db_path or utils.data_path("flick").joinpath("web_requests.json")
        self.db_file.parent.mkdir(parents=True, exist_ok=True)

    @contextlib.contextmanager
    def _requests_table(self):
        with tinydb.TinyDB(self.db_file) as db:
            yield db.table("requests")

    def insert(self, request: Request):
        with self._requests_table() as table:
            doc_id = table.insert(request.model_dump(exclude={"id"}))
            request.id = doc_id

    def get_all(self) -> List[Request]:
        with self._requests_table() as table:
            return [Request.from_document(item) for item in table.all()]

    def delete_by_id(self, doc_id: int):
        with self._requests_table() as table:
            table.remove(doc_ids=[doc_id])

    def update_request_response(self, doc_id: int, response: Response):
        with self._requests_table() as table:
            table.update({"response": response.model_dump()}, doc_ids=[doc_id])


class WebRequestService:

    def __init__(self) -> None:
        self.db_impl = TinyDbImpl()
        self.timeout = 60 * 10  # 10 minutes

    def list_request(self) -> List[Request]:
        return self.db_impl.get_all()

    def delete_request(self, doc_id: int):
        self.db_impl.delete_by_id(doc_id)

    def send_request(
        self, method: str, url: str, body: Optional[str] = None, headers: Optional[dict] = None
    ) -> Request:
        request = Request(
            id=0,
            send_time=datetime.now().isoformat(),
            method=method,
            url=url,
            headers=headers,
            body=body,
        )
        self.db_impl.insert(request)
        logger.info("Sending request: {} {}", request.method, request.url)
        try:
            raw_resp = requests.request(
                method, url, headers=headers, data=body, timeout=self.timeout
            )
        except requests.exceptions.ConnectionError as e:
            logger.error("Failed to send request: {}", e)
            raise RuntimeError(f"Failed to send request: {e}") from e
        response = Response(
            elapsed=raw_resp.elapsed.total_seconds(),
            status_code=raw_resp.status_code,
            reason=raw_resp.reason,
            headers=dict(raw_resp.headers),
            body=raw_resp.content.decode("utf-8", errors="replace") if raw_resp.content else None,
        )
        request.response = response
        self.db_impl.update_request_response(request.id, response)
        return request


SERVICE = WebRequestService()
