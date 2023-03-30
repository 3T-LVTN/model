from app.internal.dao.location import Location
from app.internal.repository.base import BaseRepo, Page
from sqlalchemy.orm import Session, Query
from sqlalchemy import func

from app.internal.repository.constants import FLOATING_POINT_THRESHOLD


class LocationFilter:
    longitude: float = None
    latitude: float = None


class LocationRepo(BaseRepo):
    def _build_filter_query(self, query: Query, filter: LocationFilter) -> Query:
        if filter.latitude is not None:
            query = query.where(func.abs(Location.latitude - filter.latitude) < FLOATING_POINT_THRESHOLD)
        if filter.longitude is not None:
            query = query.where(func.abs(Location.latitude - filter.latitude) < FLOATING_POINT_THRESHOLD)
        return query

    def filter(self, db_session: Session, filter: LocationFilter, page=None, page_size=None) -> Page[Location]:
        query = db_session.query()
        return self.paginate(self._build_filter_query(query, filter), page=page, page_size=page_size)

    def filter_all(self, db_session: Session, filter: LocationFilter) -> list[Location]:
        query = db_session.query()
        return self._build_filter_query(query, filter).all()


location_repo = LocationRepo(Location)
