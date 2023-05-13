from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped

from app.internal.dao.base import BaseModel
if TYPE_CHECKING:
    from app.internal.dao.location import Location
    from app.internal.dao.time_window import TimeWindow


class PredictedLog(BaseModel):
    '''
    for VOVE project, this table is number of mosquitto we aggregate data from specific location at specific timewindow
    In order to reuse it for another type of project i think naming it as predicted var is better
    '''
    __tablename__ = "predicted_log"

    # foreignkey
    location_id: int = Column(Integer, ForeignKey("location.id"))

    # data column
    value: int = Column(Integer)
    model_file_path: str = Column(String(50))

    ######## relationship ############
    location: Mapped['Location'] = relationship("Location", foreign_keys=[location_id], viewonly=True)

    UniqueConstraint("location_id", "time_window_id")
