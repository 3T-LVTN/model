

import logging
from app.api.request.get_prediction_request import GetPredictionRequest
from app.api.request.get_weather_detail_request import GetWeatherDetailRequest
from app.api.response.get_prediction_response import GetPredictionResponse, PredictionData
from app.api.response.get_summary_response import GetWeatherSummaryResponse, SummaryLocationInfo
from app.api.response.get_weather_detail_response import GetWeatherDetailResponse, LocationDetail, LocationDetailData, LocationDetailGeometry
from app.internal.service.dto.prediction_dto import PredictionDTO
from app.internal.repository.weather_log import weather_log_repo, WeatherLogFilter
from app.internal.service.dto.weather_detail_dto import WeatherDetailDTO
from app.internal.service.dto.weather_summary_dto import WeatherSummaryDTO
from app.internal.util.time_util import time_util


class PredictionTransformer:

    def prediction_dto_to_response(self, request: GetPredictionRequest, map_idx_to_prediction: dict
                                   [int, float]) -> GetPredictionResponse:
        response = GetPredictionResponse()
        min_weight = min([x for _, x in map_idx_to_prediction.items()])
        for location in request.locations:
            prediction = map_idx_to_prediction.get(location.idx)
            if prediction is None:
                response.data.missing_locations.append(PredictionData(
                    long=location.lng, lat=location.lat))
            else:
                # we modified our prediction data to improve contrast between district
                prediction_data = PredictionData(
                    long=location.lng, lat=location.lat, weight=prediction-min_weight+1)
                response.data.available_locations.append(prediction_data)
        return response

    def weather_log_request_to_repo_filter(self, request: GetWeatherDetailRequest) -> WeatherLogFilter:
        request.start_time = time_util.to_start_date_timestamp(request.start_time)
        request.end_time = time_util.to_start_date_timestamp(request.end_time)
        return WeatherLogFilter(
            time_gte=request.start_time,
            time_lte=request.end_time,
        )

    def summary_dto_to_summary_response(self, dto: WeatherSummaryDTO) -> GetWeatherSummaryResponse:
        resp = GetWeatherSummaryResponse()
        logging.info("summary dto", dto)
        for id, third_party_location in dto.map_location_id_to_third_party.items():
            location_info = dto.map_location_id_to_location.get(id)
            weather_info = dto.map_location_id_to_weather_log.get(id)
            predict = dto.map_location_id_to_prediction.get(id)
            summary_location_info = SummaryLocationInfo(
                location_code=third_party_location.location_code,
                lat=location_info.latitude,
                lng=location_info.longitude,
                value=predict,
                precip=weather_info.precipitation,
                temperature=weather_info.temperature
            )
            resp.data.append(summary_location_info)

        return resp

    def detail_dto_to_detail_response(self, dto: WeatherDetailDTO) -> GetWeatherDetailResponse:
        data = LocationDetailData()
        logging.info("weather detail dto", dto)
        data.location_geometry = LocationDetailGeometry(
            lat=dto.lat,
            lng=dto.long,
            location_code=dto.location_code,
        )
        map_date_to_prediction = dto.map_date_to_prediction_value
        map_date_to_log = dto.map_date_to_weather_log
        data.location_detail = [
            LocationDetail(
                date=date,
                value=map_date_to_prediction.get(date),
                temperature=map_date_to_log.get(date).temperature,
                precip=map_date_to_log.get(date).precipitation,
            ) for date in map_date_to_prediction.keys()
        ]
        return GetWeatherDetailResponse(
            data=data
        )
