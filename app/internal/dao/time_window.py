from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.internal.dao.base import BaseModel


class TimeWindow(BaseModel):
    __name__ = "time_window"

    sliding_size: int = Column(Integer)
    '''number of day we aggregate data'''

    start_ts: int = Column(Integer)
    end_ts: int = Column(Integer)

    UniqueConstraint("start_ts", "end_ts", "sliding_size")
