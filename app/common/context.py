from typing import Annotated, Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from logging import LoggerAdapter
from starlette_context import context

from app.common.logger import CustomLoggerAdapter
from app.internal.dao import db


class Context(dict):
    '''
    context for easily pass object through api call
    '''
    method: str = ""
    logger: LoggerAdapter

    def extract_logger(self, tag: str, name: str) -> LoggerAdapter:
        def attach_logger_ctx():
            try:
                old_logger = self.logger
                new_logger = CustomLoggerAdapter(old_logger,  {tag: name})
                self.logger = new_logger
                yield self.logger
            finally:
                self.logger = old_logger
        return attach_logger_ctx()

    def extract_db_session(self) -> Session:
        return self.get("db_session")

    def attach_db_session(self, db_session: Session):
        self.update({"db_session": db_session})


def get_context() -> Generator[Context, None, None]:
    ctx = context.get("ctx")
    return ctx
