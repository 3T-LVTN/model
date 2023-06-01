from abc import abstractmethod
import asyncio
import logging
from typing import Protocol
from sqlalchemy.orm import Session

from app.api.request.get_prediction_request import GetPredictionRequest
from app.api.response.get_prediction_response import GetPredictionResponse
from app.api.request.get_weather_detail_request import GetWeatherDetailRequest
from app.api.response.get_weather_detail_response import GetWeatherDetailResponse
from app.api.request.get_summary_request import GetWeatherSummaryRequest
from app.api.response.get_summary_response import GetWeatherSummaryResponse
from app.common.context import Context
from app.config import env_var
from app.internal.model.model.model import Nb2MosquittoModel
from app.internal.service.prediction_service import get_prediction
from app.internal.service.summary_service import get_weather_summary,  get_weather_detail
from app.internal.service.transformer.prediction_transformer import PredictionTransformer
from app.internal.repository.weather_log import weather_log_repo

__logger = logging.getLogger(__file__)


class IService(Protocol):
    @abstractmethod
    def get_prediction(self, ctx: Context,  request: GetPredictionRequest) -> GetPredictionResponse: ...

    @abstractmethod
    def get_weather_summary(
        self, ctx: Context, request: GetWeatherSummaryRequest) -> GetWeatherSummaryResponse: ...

    @abstractmethod
    def get_weather_detail(self, ctx: Context, request: GetWeatherDetailRequest) -> GetWeatherDetailResponse: ...


class Service(IService):

    def __init__(self) -> None:
        if env_var.IS_EXPERIMENT:
            # load list of available model
            return
        # if not experiment init first models
        self.models = [Nb2MosquittoModel(1)]
        self.transformer = PredictionTransformer()

    def get_prediction(self, ctx: Context,  request: GetPredictionRequest) -> GetPredictionResponse:
        data = get_prediction(ctx, self.models[0], request)
        return self.transformer.prediction_dto_to_response(request, data)

    def get_weather_summary(self, ctx: Context, request: GetWeatherSummaryRequest) -> GetWeatherSummaryResponse:
        weather_summary_dto = get_weather_summary(ctx, self.models[0],  request)
        __logger.info(weather_summary_dto)
        return self.transformer.summary_dto_to_summary_response(weather_summary_dto)

    def get_weather_detail(self, ctx: Context, request: GetWeatherDetailRequest) -> GetWeatherDetailResponse:
        weather_detail_dto = get_weather_detail(ctx, self.models[0], request)
        __logger.info(weather_detail_dto)
        return self.transformer.detail_dto_to_detail_response(weather_detail_dto)


service = Service()
