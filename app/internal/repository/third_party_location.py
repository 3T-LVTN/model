from pydantic import BaseModel
from sqlalchemy.orm import Session, Query, joinedload
from sqlalchemy import func
from app.internal.dao.location import Location

from app.internal.repository.constants import FLOATING_POINT_THRESHOLD
from app.internal.dao.third_party_location import ThirdPartyLocation
from app.internal.repository.base import BaseRepo, Page, BaseFilterType


class ThirdPartyLocationFilter(BaseFilterType):
    location_codes: list[str] = None


class ThirdPartyLocationRepo(BaseRepo[ThirdPartyLocation]):
    def _build_filter_query(self, query: Query, filter: ThirdPartyLocationFilter) -> Query:
        if filter.location_codes is not None:
            query = query.where(ThirdPartyLocation.location_code.in_(filter.location_codes))
        query = query.options(joinedload(ThirdPartyLocation.location))
        return query

    def filter(self, db_session: Session, filter: ThirdPartyLocationFilter, page=None, page_size=None) -> Page[
            ThirdPartyLocation]:
        query = db_session.query(ThirdPartyLocation)
        return self.paginate(
            self._build_filter_query(query, filter).order_by(ThirdPartyLocation.id),
            page=page, page_size=page_size)

    def filter_all(self, db_session: Session, filter: ThirdPartyLocationFilter) -> list[ThirdPartyLocation]:
        query = db_session.query(ThirdPartyLocation)
        return self._build_filter_query(query, filter).order_by(ThirdPartyLocation.id).all()

    def get_first(self, db_session: Session, filter: ThirdPartyLocationFilter) -> ThirdPartyLocation:
        query = db_session.query(ThirdPartyLocation)
        return self._build_filter_query(query, filter).order_by(ThirdPartyLocation.id).first()


third_party_location_repo = ThirdPartyLocationRepo(ThirdPartyLocation)
