from app.internal.dao.base import Page
from app.internal.dao.time_window import TimeWindow
from app.internal.dao.weather_log import WeatherLog
from app.internal.repository.base import BaseRepo

from sqlalchemy.orm import Session, Query
from pydantic import BaseModel


class WeatherLogFilter(BaseModel):
    # data column
    avg_rain_fall: int = None
    avg_temp: int = None
    max_temp: int = None
    min_temp: int = None
    # relationship
    time_window_sliding_size: int = None


class WeatherLogRepo(BaseRepo):
    def _build_filter_query(self, query: Query, filter: WeatherLogFilter) -> Query:
        if filter.avg_temp is not None:
            query = query.filter(WeatherLog.temperature == filter.avg_temp)
        if filter.max_temp is not None:
            query = query.filter(WeatherLog.maximum_temperature == filter.max_temp)
        if filter.min_temp is not None:
            query = query.filter(WeatherLog.minimum_temperature == filter.min_temp)
        if filter.time_window_sliding_size is not None:
            query = query.filter(WeatherLog.time_window.has(
                TimeWindow.sliding_size == filter.time_window_sliding_size))
        return query

    def filter(self, db_session: Session, filter: WeatherLogFilter, page=None, page_size=None) -> Page[WeatherLog]:
        query = db_session.query()
        return self.paginate(self._build_filter_query(query, filter), page=page, page_size=page_size)

    def filter_all(self, db_session: Session, filter: WeatherLogFilter) -> list[WeatherLog]:
        query = db_session.query()
        return self._build_filter_query(query, filter).all()


weather_log_repo = WeatherLogRepo(WeatherLog)
