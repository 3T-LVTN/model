from fastapi_camelcase import CamelModel
from pydantic import Field

from app.api.response.base import BaseResponse


class PredictionData(CamelModel):
    idx: int = None
    long: float = None
    lat: float = None
    weight: int = None  # None mean no prediction for this one


class GetPredictionResponseData(CamelModel):
    available_locations: list[PredictionData] = Field(default_factory=list)
    missing_locations: list[PredictionData] = Field(default_factory=list)


class GetPredictionResponse(BaseResponse):
    data: GetPredictionResponseData = Field(default_factory=GetPredictionResponseData)
