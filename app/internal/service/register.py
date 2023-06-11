from abc import abstractmethod
import asyncio
import logging
from typing import Protocol
from sqlalchemy.orm import Session

from app.api.request.get_prediction_request import GetPredictionRequest
from app.api.response.common import Rate
from app.api.response.get_prediction_response import GetPredictionResponse
from app.api.request.get_weather_detail_request import GetWeatherDetailRequest
from app.api.response.get_weather_detail_response import GetWeatherDetailResponse
from app.api.request.get_summary_request import GetWeatherSummaryRequest
from app.api.response.get_summary_response import GetHCMCProviceSummaryResponse, GetWeatherSummaryResponse, HCMCSummaryResponseData
from app.common.context import Context
from app.config import env_var
from app.internal.model.model.model import Nb2MosquittoModel
from app.internal.repository.ward import ward_repo
from app.internal.service.common import predict_with_location_ids
from app.internal.service.prediction_service import get_prediction
from app.internal.service.summary_service import get_weather_summary,  get_weather_detail
from app.internal.service.transformer.prediction_transformer import PredictionTransformer
from app.internal.repository.weather_log import weather_log_repo
from app.internal.util.time_util import time_util

_logger = logging.getLogger()


class IService(Protocol):
    @abstractmethod
    def get_prediction(self, ctx: Context,  request: GetPredictionRequest) -> GetPredictionResponse: ...

    @abstractmethod
    def get_weather_summary(
        self, ctx: Context, request: GetWeatherSummaryRequest) -> GetWeatherSummaryResponse: ...

    @abstractmethod
    def get_weather_detail(self, ctx: Context, request: GetWeatherDetailRequest) -> GetWeatherDetailResponse: ...

    @abstractmethod
    def get_hcmc_summary(self, ctx: Context) -> GetHCMCProviceSummaryResponse: ...


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
        _logger.info(weather_summary_dto)
        return self.transformer.summary_dto_to_summary_response(request, weather_summary_dto)

    def get_weather_detail(self, ctx: Context, request: GetWeatherDetailRequest) -> GetWeatherDetailResponse:
        weather_detail_dto = get_weather_detail(ctx, self.models[0], request)
        if weather_detail_dto is None:
            return GetWeatherDetailResponse()
        _logger.info(weather_detail_dto)
        return self.transformer.detail_dto_to_detail_response(weather_detail_dto)

    def get_hcmc_summary(self, ctx: Context) -> GetHCMCProviceSummaryResponse:
        db_session = ctx.extract_db_session()
        wards = ward_repo.get_all(db_session)

        map_location_id_to_location = {ward.location_id: ward.location for ward in wards}
        _, map_location_to_quartile = predict_with_location_ids(
            ctx=ctx, model=self.models[0], location_ids=list(map_location_id_to_location.keys()),
            time=time_util.datetime_to_ts(time_util.now()))
        ward_rate_list = [0]*4
        for ward in wards:
            ward_rate_list[map_location_to_quartile.get(ward.location_id)] += 1

        return GetHCMCProviceSummaryResponse(
            data=HCMCSummaryResponseData(
                **{val: ward_rate_list[idx] for idx, val in enumerate(Rate.__members__)}))


service = Service()
