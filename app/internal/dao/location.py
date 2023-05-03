from sqlalchemy import Column, String, Float, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING

from app.internal.dao.base import BaseModel
if TYPE_CHECKING:
    from app.internal.dao.weather_log import WeatherLog


class Location(BaseModel):
    __tablename__ = "location"

    longitude = Column(Float)
    latitude = Column(Float)

    weather_log: Mapped[list['WeatherLog']] = relationship(viewonly=True)
