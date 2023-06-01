from typing import Annotated, Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from logging import LoggerAdapter, getLogger
from starlette_context import context

from app.common.logger import CustomLoggerAdapter
from app.internal.dao import db

_logger = getLogger()


class Context(dict):
    '''
    context for easily pass object through api call
    '''
    method: str = ""

    def extract_db_session(self) -> Session:
        return self.get("db_session")

    def attach_db_session(self, db_session: Session):
        self.update({"db_session": db_session})


def get_context() -> Generator[Context, None, None]:
    ctx = context.get("ctx")
    return ctx
