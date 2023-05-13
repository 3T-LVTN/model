from sqlalchemy.orm import Session, Query
from pydantic import BaseModel
from app.internal.dao.time_window import TimeWindow
from app.internal.repository.base import BaseRepo
from app.internal.util.time_util import time_util


class TimeWindowFilter(BaseModel):
    min_datetime_ts: int = None   # filter timewindow has start ts >= filter
    max_datetime_ts: int = None   # filter timewindow has end ts <= filter
    eq_start_date_ts: int = None  # filter min ts is in the same date with that time window start ts
    eq_end_date_ts: int = None    # filter max ts is in the same date with that time window end ts


class TimeWindowRepo(BaseRepo[TimeWindow]):
    def _build_query(self, base_query: Query, filter: TimeWindowFilter) -> Query:
        query = base_query
        if filter.min_datetime_ts is not None:
            min_ts = time_util.to_start_date_timestamp(filter.min_datetime_ts)
            query = query.filter(TimeWindow.start_ts <= min_ts)
        if filter.max_datetime_ts is not None:
            max_ts = time_util.to_end_date_timestamp(filter.max_datetime_ts)
            query = query.filter(TimeWindow.end_ts <= max_ts)
        if filter.eq_start_date_ts is not None:
            min_ts = time_util.to_start_date_timestamp(filter.eq_start_date_ts)
            query = query.filter(TimeWindow.start_ts == min_ts)
        if filter.eq_end_date_ts is not None:
            max_ts = time_util.to_end_date_timestamp(filter.eq_end_date_ts)
            query = query.filter(TimeWindow.end_ts == max_ts)
        return query

    def get_first(self, db_session: Session, filter: TimeWindowFilter) -> TimeWindow:
        return self._build_query(db_session.query(TimeWindow), filter).order_by(TimeWindow.id).first()


time_window_repo = TimeWindowRepo(TimeWindow)
