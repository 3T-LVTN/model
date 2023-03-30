from app.adapter.base import BaseAdapter
from app.middleware.router.dto import WebhookConfig, ErrorMessage, INFO_COLOR, Payload


class SlackMessageAdapter(BaseAdapter):
    mention_users = "cloudythy"

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
            info._color = INFO_COLOR
        error_msg = error.get_message()

        payload = Payload(
            text=f'{error_msg} {" ".join([f"<@{user}>" for user in self.mention_users])}',
            channel=self.cfg.channel,
            attachments=error
        )

        self.post(payload.json())
