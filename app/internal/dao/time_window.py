from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped
from typing import TYPE_CHECKING
from app.internal.dao.base import BaseModel
if TYPE_CHECKING:
    from app.internal.dao.weather_log import WeatherLog


class TimeWindow(BaseModel):
    __tablename__ = "time_window"

    sliding_size: int = Column(Integer)
    '''number of day we aggregate data'''

    start_ts: int = Column(Integer)
    end_ts: int = Column(Integer)

    weather_log: Mapped[list['WeatherLog']] = relationship(viewonly=True)

    UniqueConstraint("start_ts", "end_ts", "sliding_size")
