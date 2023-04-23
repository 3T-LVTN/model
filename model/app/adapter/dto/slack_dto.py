from abc import ABC, abstractmethod
from pydantic import BaseModel, Protocol
from typing import Optional

EXCEPTION_COLOR = "#dc3545"
INFO_COLOR = "#0000de"


class WebhookConfig(BaseModel):
    ''' url for webhook, channel and env for notification '''
    url: str
    channel: str
    env: str


class AttachmentField(BaseModel):
    '''attachment in slack message, currently is title(of this field) and currently value is message only'''
    title: str
    value: str


class Attachment(BaseModel):
    color: Optional[str]
    text: Optional[str]
    '''attachment title, should indicate where error is or error title'''
    fields: Optional[list[AttachmentField]]
    '''fields include in attachment, mostly request and response'''
    mrkdwn_in: Optional[list[str]] = ["text", "fields"]
    '''indicates fields should be treated as markdown format'''


class Payload(BaseModel):
    channel: Optional[str]
    username: Optional[str]
    text: Optional[str]
    attachments: Optional[list[Attachment]]
    mrkdwn: Optional[bool] = True


class ErrorMessage(ABC):
    @abstractmethod
    def get_attachments(self) -> list[Attachment]: ...
    @abstractmethod
    def get_message(self) -> str: ...
