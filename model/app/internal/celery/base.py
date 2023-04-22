import celery
from app.internal.celery.celery import celery_app
from app.adapter.slack_adapter import slack_adapter, ErrorMessage
from app.adapter.dto.slack_dto import Attachment


class BaseTask(celery.Task):
    class CeleryTasksException(ErrorMessage):

        def __init__(self, error: Exception, task_id: int, args, kwargs) -> None:
            self.error = error
            attachment = [Attachment(text="EXCEPTION", value=error.__repr__()),
                          Attachment(text="TASK_ID", value=task_id),
                          Attachment(text="TASK ARGUMENTS", value=str(args)),
                          Attachment(text="TASK KEYWORD ARGUMENTS", value=str(kwargs)),]
            self.attachements = attachment

        def get_attachments(self) -> list[Attachment]:
            return self.attachements

        def get_message(self) -> str:
            return f"encounter {self.error.__str__()}"

    def on_failure(self, error, task_id, args, kwargs, einfo):
        slack_adapter.send_error(BaseTask.CeleryTasksException(error=error, task_id=task_id, args=args, kwargs=kwargs))
