from typing import Any
from app.adapter.slack_adapter import slack_adapter
from app.adapter.dto.slack_dto import Attachment, ErrorMessage


class TestSlack:
    def test_diss_hoe(self):
        class SlackTestDTO(ErrorMessage):
            def __init__(self, body: Any = None,  params: Any = None) -> None:
                attachment = [Attachment(text="du hoe", value="hoe thy")]
                self.attachements = attachment

            def get_attachments(self) -> list[Attachment]:
                return self.attachements

            def get_message(self) -> str:
                return "encounter hoe thy"

        slack_adapter.send_error(SlackTestDTO())
