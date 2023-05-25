
import asyncio
from dataclasses import dataclass
import datetime
import logging
from typing import Coroutine, Iterable
import numpy as np

from app.api.request.get_summary_request import GetWeatherSummaryRequest
from app.api.request.get_weather_detail_request import GetWeatherDetailRequest
from app.common.context import Context
from app.common.exception import ThirdServiceException
from app.api.request.get_summary_request import Location as RequestLocation
from app.internal.dao.location import Location
from app.internal.dao.third_party_location import ThirdPartyLocation
from app.internal.dao.weather_log import WeatherLog
from app.internal.model.model.model import Nb2MosquittoModel
from app.internal.repository.location import LocationFilter, location_repo
from app.internal.repository.weather_log import WeatherLogFilter, weather_log_repo
from app.internal.service.dto.prediction_dto import PredictionDTO
from app.internal.service.dto.weather_detail_dto import WeatherDetailDTO
from app.internal.service.dto.weather_summary_dto import WeatherSummaryDTO
from app.internal.repository.third_party_location import third_party_location_repo, ThirdPartyLocationFilter
from app.internal.util.time_util import time_util


def _find_location_by_long_lat(ctx: Context, location_request: RequestLocation) -> tuple[Location, ThirdPartyLocation]:
    db_session = ctx.extract_db_session()

    # find the location we are currently refer to
    location = location_repo.get_first(db_session=db_session, filter=LocationFilter(
        longitude=location_request.lng,
        latitude=location_request.lat
    ))
    # if this is new location create new record in db
    if location is None:
        location = location_repo.save(db_session, Location(
            longitude=location_request.lng,
            latitude=location_request.lat,
        ))
    # cache this location code
    third_party_location = third_party_location_repo.save(db_session, ThirdPartyLocation(
        location_code=location_request.location_code,
        location_id=location.id
    ))
    return location, third_party_location


async def predict_with_location_ids(ctx: Context, model: Nb2MosquittoModel, location_ids: Iterable[int]) -> dict[int, float]:
    db_session = ctx.extract_db_session()
    map_location_id_to_prediction: dict[int, float] = {}
    for location in location_ids:
        map_location_id_to_prediction.update({location: model.predict_with_location_id(
            db_session=db_session, location_id=location,
            date_time=time_util.datetime_to_ts(time_util.now())).count})
    return map_location_id_to_prediction


async def get_weather_log_with_location_ids(ctx: Context, location_ids: Iterable[int]) -> dict[int, WeatherLog]:
    db_session = ctx.extract_db_session()
    weather_logs = weather_log_repo.filter_all(db_session=db_session, filter=WeatherLogFilter(
        location_ids=location_ids
    ))
    map_location_id_to_weather_log = {log.location_id: log for log in weather_logs}
    return map_location_id_to_weather_log


async def get_weather_summary(ctx: Context, model: Nb2MosquittoModel, request: GetWeatherSummaryRequest) -> WeatherSummaryDTO:
    db_session = ctx.extract_db_session()

    map_location_id_to_third_party: dict[int, ThirdPartyLocation] = {}
    map_location_id_to_location: dict[int, Location] = {}

    third_party_locations = third_party_location_repo.filter_all(db_session, ThirdPartyLocationFilter(
        location_codes=[location.location_code for location in request.locations]
    ))
    map_location_id_to_third_party = {location.location_id: location for location in third_party_locations}
    map_location_id_to_location = {location.location.id: location.location for location in third_party_locations}
    location_codes = [location.location_code for location in third_party_locations]
    for location in request.locations:
        if location.location_code not in location_codes:
            internal_location, third_party_location = _find_location_by_long_lat(ctx, location)
            map_location_id_to_third_party.update({internal_location.id: third_party_location})
            map_location_id_to_location.update({internal_location.id: internal_location})

    map_location_id_to_prediction = await predict_with_location_ids(
        ctx=ctx, model=model, location_ids=map_location_id_to_location.keys())

    map_location_id_to_weather_log = await get_weather_log_with_location_ids(ctx, map_location_id_to_location.keys())

    return WeatherSummaryDTO(
        map_location_id_to_weather_log=map_location_id_to_weather_log,
        map_location_id_to_prediction=map_location_id_to_prediction,
        map_location_id_to_third_party=map_location_id_to_third_party,
        map_location_id_to_location=map_location_id_to_location,
    )


async def get_prediction_for_date(ctx: Context, model: Nb2MosquittoModel, location_id: int, date: int) -> float:
    db_session = ctx.extract_db_session()
    prediction = model.predict_with_location_id(location_id=location_id, date_time=date, db_session=db_session)
    return prediction.count


def get_map_date_to_weather_log(ctx: Context, model: Nb2MosquittoModel, location_id: int, start_time: int,
                                end_time: int) -> dict[int, WeatherLog]:
    db_session = ctx.extract_db_session()

    weather_logs = weather_log_repo.filter_all(db_session=db_session, filter=WeatherLogFilter(
        time_gte=start_time,
        time_lte=end_time,
    ))
    weather_logs.sort(key=lambda x: x.date_time)
    start_time_dt = time_util.ts_to_datetime(start_time)
    time_interval = time_util.ts_to_datetime(end_time) - start_time_dt
    return {
        time_util.datetime_to_ts(start_time_dt+datetime.timedelta(i)): weather_logs[i] for i in range(time_interval.days)
    }


def get_map_date_to_prediction(
        ctx: Context, model: Nb2MosquittoModel, location_id: int, start_time: int, end_time: int) -> dict[
        int, float]:
    db_session = ctx.extract_db_session()
    start_time_dt = time_util.ts_to_datetime(start_time)
    time_interval = time_util.ts_to_datetime(end_time) - start_time_dt
    predictions = model.predict_for_time_interval(
        location_id=location_id, start_time=start_time, end_time=end_time, db_session=db_session)
    return {
        time_util.datetime_to_ts(start_time_dt+datetime.timedelta(i)): predictions[i] for i in range(time_interval.days)
    }


async def get_weather_detail(ctx: Context, model: Nb2MosquittoModel,
                             request: GetWeatherDetailRequest) -> WeatherDetailDTO:
    logger = ctx.extract_logger()
    db_session = ctx.extract_db_session()

    internal_location, third_party_location = _find_location_by_long_lat(
        ctx, RequestLocation(lat=request.lat, long=request.lng))

    map_date_to_prediction = get_map_date_to_prediction(
        ctx, model, location_id=internal_location.id, start_time=request.start_time, end_time=request.end_time)
    map_date_to_weather_log = get_map_date_to_weather_log(
        ctx, model, location_id=internal_location.id, start_time=request.start_time, end_time=request.end_time)

    return WeatherDetailDTO(
        lat=request.lat,
        long=request.lng,
        location_code=third_party_location.location_code,
        map_date_to_prediction_value=map_date_to_prediction,
        map_date_to_weather_log=map_date_to_weather_log,
    )
