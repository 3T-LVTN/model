import json
import logging
from app.adapter.base import BaseAdapter
from app.adapter.dto.slack_dto import WebhookConfig, ErrorMessage, INFO_COLOR, Payload
from app.config import env_var


class SlackMessageAdapter(BaseAdapter):
    mention_users = ["cloudythy"]

    def __init__(self, cfg: WebhookConfig) -> None:
        super().__init__(url=cfg.url, name="SLACK")
        self.cfg = cfg
        self.url = self.cfg.url

    def send_error(self, error: ErrorMessage):
        '''
        - error: error encounter
        - attachment:currently is request and error, no traceback attach
        '''

        error_info = error.get_attachments()
        for info in error_info:
            info.color = INFO_COLOR
        error_msg = json.dumps(error.get_message())

        payload = Payload(
            text=f'{error_msg} {" ".join([f"<@{user}>" for user in self.mention_users])}',
            channel=self.cfg.channel,
            attachments=error.get_attachments()
        )

        self.post(payload=payload)


cfg = WebhookConfig(
    env=env_var.ENVIRONMENT,
    url=env_var.SLACK_WEBHOOK_URL,
    channel=env_var.SLACK_ALERT_CHANNEL_NAME,
)
slack_adapter = SlackMessageAdapter(cfg=cfg)
