import datetime
import json
import time
from typing import Any, Callable, Union
from fastapi import APIRouter
from fastapi.routing import APIRoute
from fastapi import Request, Response
from starlette.responses import UJSONResponse
from app.middleware.router.slack_adapter import SlackMessageAdapter, WebhookConfig
from app.middleware.router.dto import Attachment, ErrorMessage
from app.internal.dao import db
from app.config import env_var
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class ApiException(ErrorMessage):

    def __init__(self, error: Exception, body: Any,  params=Any) -> None:
        self.error = error
        attachment = [Attachment(text="REQUEST BODY", value=body),
                      Attachment(text="REQUEST PARAM", value=params)]
        self.attachements = attachment

    def get_attachments(self) -> list[Attachment]:
        return self.attachements

    def get_message(self) -> str:
        return f"encounter {self.error.__str__()}"


cfg = WebhookConfig(
    env=env_var.ENVIRONMENT,
    url=env_var.SLACK_WEBHOOK_URL,
)
api_error_notify = SlackMessageAdapter(cfg=cfg)


class CustomAPIRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Union[Response, UJSONResponse]:
            resp = None
            e = None
            try:
                resp = await original_route_handler(request)
                return resp
            except Exception as exc:
                e = exc
                raise exc
            finally:
                # end_time = datetime.datetime.strftime(datetime.datetime.now(), DATETIME_FORMAT)
                req_body = json.loads(await request.body())
                db_session = next(db.get_db_session())

                if e:
                    err = ApiException(error=e, body=req_body, params=request.query_params)
                    api_error_notify.send_error(error=err)

                db_session.close()
        return custom_route_handler


class CustomAPIRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        if not kwargs.get("route_class"):
            self.route_class = CustomAPIRoute
