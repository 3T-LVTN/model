from sqlalchemy import Column, Integer
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import JSON
from app.internal.dao.base import BaseModel


class PredictionQuartile(BaseModel):

    __tablename__ = 'prediction_quartile'

    time: int = Column(Integer, comment="start time of quartile date")

    quartile_threshold: list[int] = Column(
        MutableList.as_mutable(JSON),
        comment="array of 3 float that devide  threshold")
