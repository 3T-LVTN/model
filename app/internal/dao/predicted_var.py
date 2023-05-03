from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped

from app.internal.dao.base import BaseModel
if TYPE_CHECKING:
    from app.internal.dao.location import Location
    from app.internal.dao.time_window import TimeWindow


class PredictedVar(BaseModel):
    '''
    for VOVE project, this table is number of mosquitto we aggregate data from specific location at specific timewindow
    In order to reuse it for another type of project i think naming it as predicted var is better
    '''
    __tablename__ = "predicted_var"

    # foreignkey
    location_id: int = Column(Integer, ForeignKey("location.id"))
    time_window_id: int = Column(Integer, ForeignKey("time_window.id"))

    # data column
    date_time: int = Column(Integer)
    value: int = Column(Integer)

    ######## relationship ############
    location: Mapped['Location'] = relationship("Location", foreign_keys=[location_id], viewonly=True)
    time_window: Mapped['TimeWindow'] = relationship("TimeWindow", foreign_keys=[time_window_id], viewonly=True)
