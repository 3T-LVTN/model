from fastapi_camelcase import CamelModel
from pydantic import Field


class PredictLocation(CamelModel):
    lng: float = Field(alias="long")
    lat: float
    idx: int
    location_code: str = None


class GetPredictionRequest(CamelModel):
    predict_date: int  # timestamp
    locations: list[PredictLocation]
