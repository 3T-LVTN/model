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
    __name__: str
    __allow_unmapped__ = True

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def as_dict(self) -> dict:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def __init__(self, **kwargs) -> None:
        for key, arg in kwargs.items():
            if not key.startswith('_') and hasattr(self, key):
                setattr(self, key, arg)


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, created_by: str = None, updated_by: str = None, **kwargs):
        super().__init__(**kwargs)
        self.created_by: str = created_by
        self.updated_by: str = updated_by
