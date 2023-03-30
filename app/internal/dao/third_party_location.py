from sqlalchemy import Column, String, Double
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

from app.internal.dao.base import Base
if TYPE_CHECKING:
    from app.internal.dao.location import Location


class ThirdPartyLocation(Base):
    '''may not need this class as we do not support get data from google to draw'''
    __name__ = "third_party_location"

    service_name: str = Column(String(50))

    longitude = Column(Double, primary_key=True)
    latitude = Column(Double, primary_key=True)

    location: 'Location' = relationship('Location', foreign_keys=[longitude, latitude])
