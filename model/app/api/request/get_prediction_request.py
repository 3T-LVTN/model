from fastapi_camelcase import CamelModel


class PredictLocation(CamelModel):
    long: float
    lat: float
    idx: int


class GetPredictionRequest(CamelModel):
    predictDate: int  # timestamp
    locations: list[PredictLocation]
