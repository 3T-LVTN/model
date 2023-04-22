from dataclasses import dataclass
from sqlalchemy.orm import Session
from logging import LoggerAdapter
from contextlib import contextmanager

from app.common.logger import CustomLoggerAdapter
from app.internal.model.model.model import Nb2MosquittoModel


class Context(dict):
    '''
    context for easily pass object through api call
    currently we do not implemented A|B testing, model only use our first time window
    '''
    method: str
    db_session: Session
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
        return self.db_session
