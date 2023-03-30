from abc import ABC
from typing import Any, Union

import requests

from app.common.constant import SUCCESS_STATUS_CODE


class BaseResponse(ABC):
    code: int
    message: str
    data: Any


class BaseAdapter(ABC):
    url: str
    name: str

    def __init__(self, url: str, name: str) -> None:
        self.url = url
        self.name = name

    def _to_api_url(self, end_point: str) -> str:
        if end_point.startswith("/"):
            return f"{self.url}{end_point}"
        return f"{self.url}/{end_point}"

    def _get_response(self, third_party_resp: requests.Response) -> BaseResponse:
        resp = BaseResponse()
        if third_party_resp.status_code != SUCCESS_STATUS_CODE:
            resp.code = third_party_resp.status_code
            calling_url = third_party_resp.request.url
            message = f"call to third party {self.name} api {calling_url} failed"
            resp.message = message
        else:
            resp.code = third_party_resp.status_code
            calling_url = third_party_resp.request.url
            resp.message = f"call to third party {self.name} api {calling_url} success"
            resp.data = third_party_resp.content
        return resp

    def post(self, end_point: str = "", payload: Union[dict[Any, Any], list[Any]] = None) -> BaseResponse:
        url = self._to_api_url(end_point)
        return self._get_response(requests.post(url=url, json=payload))

    def get(self, end_point: str = "", params: Union[list[Any], dict[Any, Any]] = None) -> BaseResponse:
        url = self._to_api_url(end_point)
        return self._get_response(requests.get(url=url, params=params, stream=True))
