from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, String, inspect
from sqlalchemy.orm import as_declarative, declared_attr
from typing import Any, List, TypeVar, Generic

T = TypeVar('T')


class Page(Generic[T]):
    def __init__(
        self,
        current_page: int,
        total_pages: int,
        total_items: int,
        page_size: int,
        content: List[T] = None,
    ):
        self.current_page = current_page
        self.total_pages = total_pages
        self.total_items = total_items
        self.page_size = page_size
        self.content = content


@as_declarative()
class Base:
    __abstract__ = True
    __allow_unmapped__ = True

    def as_dict(self) -> dict:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(Integer, default=lambda: int(datetime.now().timestamp()), index=True)
    updated_at = Column(
        Integer, default=lambda: int(datetime.now().timestamp()),
        onupdate=lambda: int(datetime.now().timestamp()))

    def __init__(self,  **kwargs):
        for key, arg in kwargs.items():
            if not key.startswith('_') and hasattr(self, key):
                if isinstance(arg, datetime):
                    arg = int(arg.timestamp())
                if isinstance(arg, str) and len(arg) == 0:
                    arg = None
                setattr(self, key, arg)
