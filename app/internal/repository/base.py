from datetime import datetime
from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import func
from sqlalchemy.orm import Query, Session

from app.internal.dao.base import BaseModel, Page
from app.common.constant import *

ModelType = TypeVar("ModelType")
SimpleFilterType = TypeVar("SimpleFilterType")


class BaseRepo(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_by_id(self, session: Session, id: int) -> Optional[ModelType]:
        return session.query(self.model).get(id)

    def get_all(self,   session: Session, query: Query = None) -> List[ModelType]:

        if query is None:
            return session.query(self.model).all()
        return query.all()

    @staticmethod
    def paginate(
            query: Query,
            page: int = DEFAULT_PAGE,
            page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Page:
        total_items = query.with_entities(func.count()).order_by(None).scalar()
        if page == 0:
            page = 1
        items = query.offset(page_size * (page - 1)).limit(page_size).all()
        total_pages = (total_items - 1) // page_size + 1
        return Page(
            current_page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_items=total_items,
            content=items,
        )

    @staticmethod
    def save(session: Session, model: ModelType) -> ModelType:
        session.add(model)
        session.commit()
        session.refresh(model)
        return model

    @staticmethod
    def save_all(session: Session, models: List[ModelType]) -> List[ModelType]:
        session.add_all(models)
        session.commit()
        for model in models:
            session.refresh(model)
        return models

    def delete_by_id(self, session: Session, id: int) -> ModelType:
        model: ModelType = session.query(self.model).get(id)
        if model is None:
            return None
        session.delete(model)
        session.commit()
        return model

    @staticmethod
    def delete(session: Session, model: ModelType) -> ModelType:
        session.delete(model)
        session.commit()
        return model
