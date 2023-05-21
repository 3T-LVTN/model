from app.internal.dao.base import Page
from app.internal.dao.time_window import TimeWindow
from app.internal.dao.predicted_log import PredictedLog
from app.internal.repository.base import BaseRepo, BaseFilterType

from sqlalchemy.orm import Session, Query
from pydantic import BaseModel
from sqlalchemy import func, asc, desc


class PredictedLogFilter(BaseFilterType):
    location_id: int = None
    created_at_lt: int = None
    created_at_gt: int = None
    time_window_id: int = None


class PredictedLogRepo(BaseRepo):
    def build_query(self, query: Query,  filter: PredictedLogFilter) -> Query:
        if filter is None:
            return query
        if filter.location_id is not None:
            query = query.where(PredictedLog.location_id == filter.location_id)
        if filter.created_at_lt is not None:
            query = query.where(PredictedLog.created_at < filter.created_at_lt)
        if filter.created_at_gt is not None:
            query = query.where(PredictedLog.created_at > filter.created_at_gt)

        return query

    def first(self, db_session: Session, filter: PredictedLogFilter) -> PredictedLog:
        query = db_session.query(PredictedLog)
        query = self.build_query(query, filter).order_by(desc(PredictedLog.created_at))
        return query.first()


predicted_log_repo = PredictedLogRepo(PredictedLog)
