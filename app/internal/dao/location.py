from sqlalchemy import Column, String, Float, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING

from app.internal.dao.base import BaseModel
if TYPE_CHECKING:
    from app.internal.dao.third_party_location import ThirdPartyLocation
    from app.internal.dao.weather_log import WeatherLog


class Location(BaseModel):
    __name__ = "location"

    longitude = Column(DECIMAL, ForeignKey('third_pary_location.longitude'))
    latitude = Column(DECIMAL, ForeignKey('third_pary_location.latitude'))

    third_party_locations: list['ThirdPartyLocation'] = relationship('ThirdPartyLocation')
    weather_log: list['WeatherLog'] = relationship('WeatherLog')
