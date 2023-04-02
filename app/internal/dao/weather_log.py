from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, ForeignKey, Float, String, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped

from app.internal.dao.base import BaseModel
if TYPE_CHECKING:
    from app.internal.dao.location import Location
    from app.internal.dao.time_window import TimeWindow


class WeatherLog(BaseModel):
    __tablename__ = "weather_log"

    # foreignkey
    location_id: int = Column(Integer, ForeignKey("location.id"))
    time_window_id: int = Column(Integer, ForeignKey("time_window.id"))

    # data column
    date_time: int = Column(Integer)  # timestamp
    minimum_temperature = Column(Float)
    maximum_temperature = Column(Float)
    temperature = Column(Float)
    dew_point = Column(Float)
    relative_humidity = Column(Float)
    heat_index = Column(Float)
    wind_speed = Column(Float)
    wind_gust = Column(Float)
    wind_direction = Column(Float)
    wind_chill = Column(Float)
    precipitation = Column(Float)
    precipitation_cover = Column(Float)
    snow_depth = Column(Float)
    visibility = Column(Float)
    cloud_cover = Column(Float)
    sea_level_pressure = Column(Float)
    weather_type = Column(String(500))
    info = Column(String(50))
    conditions = Column(String(500))

    ######## relationship ############
    location: Mapped['Location'] = relationship(viewonly=True)
    time_window: Mapped['TimeWindow'] = relationship(viewonly=True)
