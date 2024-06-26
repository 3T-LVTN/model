import json
from typing import List, Tuple, Dict
from http import HTTPStatus
from datetime import datetime
import uuid
from fastapi_camelcase import CamelModel, BaseModel
from typing import Any, Union
from fastapi.encoders import jsonable_encoder
import requests
import logging

from app.common.constant import SUCCESS_STATUS_CODE


class BaseResponse(CamelModel):
    code: int = None
    message: str = None
    data: Any = None

    class Config:
        arbitrary_types_allowed = True


class BaseAdapter:
    url: str
    name: str

    def __init__(self, url: str, name: str) -> None:
        self.url = url
        self.name = name

    def _to_api_url(self, end_point: str) -> str:
        if end_point.startswith("/"):
            return f"{self.url}{end_point}"
        if len(end_point) == 0:
            return self.url
        return f"{self.url}/{end_point}"

    def _get_response(self, third_party_resp: requests.Response) -> BaseResponse:
        resp = BaseResponse()
        logging.info(third_party_resp)
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
        logging.info(resp)
        return resp

    def post(self, end_point: str = "", payload: BaseModel = None) -> BaseResponse:
        url = self._to_api_url(end_point)
        headers = {'Content-type': 'application/json'}
        resp = self._get_response(requests.post(url=url, json=json.loads(payload.json()), headers=headers))
        logging.info(payload.json())
        logging.info(url)
        return resp

    def get(self, end_point: str = "", params: BaseModel = None) -> BaseResponse:
        url = self._to_api_url(end_point)
        logging.info(params)
        return self._get_response(requests.get(url=url, params=jsonable_encoder(params), stream=True))
