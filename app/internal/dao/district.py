from typing import TYPE_CHECKING
from sqlalchemy import Column, String, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped

from app.internal.dao.base import BaseModel
if TYPE_CHECKING:
    from app.internal.dao.location import Location
    from app.internal.dao.ward import Ward


class District(BaseModel):
    '''
    we do not use optimized database for location data so we use this as cache for our location data
    we use this to query by location code instead of inefficiency query by lng and lat
    '''
    __tablename__ = "district"

    location_code = Column(type_=String(255), index=True, unique=True)
    location_id = Column(Integer, ForeignKey("location.id"), index=True)

    location: Mapped['Location'] = relationship("Location", foreign_keys=[location_id], viewonly=True)
    wards: Mapped['Ward'] = relationship('Ward')
