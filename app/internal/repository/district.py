from app.internal.dao.district import District
from app.internal.repository.base import BaseRepo


class DistrictRepo(BaseRepo[District]):
    ...


district_repo = DistrictRepo(District)
