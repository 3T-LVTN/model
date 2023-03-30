from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped

from app.internal.dao.base import BaseModel
if TYPE_CHECKING:
    from app.internal.dao.location import Location
    from app.internal.dao.time_window import TimeWindow


class WeatherLog(BaseModel):
    __name__ = "weather_log"

    # foreignkey
    location_id: int = Column(Integer, ForeignKey("location.id"))
    time_window_id: int = Column(Integer, ForeignKey("time_window.id"))

    # data column
    address: str
    date_time: str
    minimum_temperature: str
    maximum_temperature: str
    temperature: str
    dew_point: str
    relative_humidity: str
    heat_index: str
    wind_speed: str
    wind_gust: str
    wind_direction: str
    wind_chill: str
    precipitation: str
    precipitation_cover: str
    snow_depth: str
    visibility: str
    cloud_cover: str
    sea_level_pressure: str
    weather_type: str
    latitude: str
    longitude: str
    resolved_address: str
    name: str
    info: str
    conditions: str

    ######## relationship ############
    location: Mapped['Location'] = relationship("Location", foreign_keys=[location_id])
    time_window: Mapped['TimeWindow'] = relationship("TimeWindow", foreign_keys=[time_window_id])

    UniqueConstraint("location_id", "time_window_id")
