from app.internal.dao.ward import Ward
from app.internal.repository.base import BaseRepo


class WardRepo(BaseRepo[Ward]):
    ...


ward_repo = WardRepo(Ward)
