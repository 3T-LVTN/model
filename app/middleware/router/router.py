import datetime
import json
import logging
import time
from typing import Any, Callable, Union
from fastapi import APIRouter
from fastapi.routing import APIRoute
from fastapi import Request, Response
from starlette.responses import UJSONResponse
from app.adapter.dto.slack_dto import Attachment, AttachmentField, ErrorMessage
from app.internal.dao import db
from app.adapter.slack_adapter import slack_adapter
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class ApiException(ErrorMessage):

    def __init__(self, error: Exception, body: Any = "",  params: Any = "") -> None:
        self.error = error
        attachment_fields = [AttachmentField(title="REQUEST BODY", value=str(body)),
                             AttachmentField(title="REQUEST PARAM", value=str(params))]
        self.attachement = [Attachment(fields=attachment_fields)]

    def get_attachments(self) -> list[Attachment]:
        return self.attachement

    def get_message(self) -> str:
        return f"encounter {self.error.__str__()}"


class CustomAPIRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Union[Response, UJSONResponse]:
            resp = None
            e = None
            logging.info("receive request", request)
            try:
                resp = await original_route_handler(request)
                return resp
            except Exception as exc:
                e = exc
                raise exc
            finally:
                # end_time = datetime.datetime.strftime(datetime.datetime.now(), DATETIME_FORMAT)
                req_body = None
                try:
                    req_body = await request.body()
                    req_body = json.loads(req_body)
                except Exception as exc:
                    logging.info(exc)
                    # in some case request body may not be loads
                    logging.info(req_body)
                    req_body = None

                if e:
                    err = ApiException(error=e, body=req_body, params=request.query_params)
                    slack_adapter.send_error(error=err)

        return custom_route_handler


class CustomAPIRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        if not kwargs.get("route_class"):
            self.route_class = CustomAPIRoute
