from typing import TYPE_CHECKING
from sqlalchemy import Column, String, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped

from app.internal.dao.base import BaseModel
if TYPE_CHECKING:
    from app.internal.dao.location import Location
    from app.internal.dao.district import District


class Ward(BaseModel):
    '''
    we do not use optimized database for location data so we use this as cache for our location data
    we use this to query by location code instead of inefficiency query by lng and lat
    '''
    __tablename__ = "ward"

    location_code = Column(type_=String(255), index=True, unique=True)
    location_id = Column(Integer, ForeignKey("location.id"), index=True)
    lat: float = Column(Float)
    lng: float = Column(Float)
    district_code = Column(String, ForeignKey("district.location_code"), index=True)
    location: Mapped['Location'] = relationship("Location", foreign_keys=[location_id], viewonly=True, lazy="immediate")
    district: Mapped['District'] = relationship("District", foreign_keys=[district_code], viewonly=True)
