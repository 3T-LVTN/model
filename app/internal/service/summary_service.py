
import asyncio
from dataclasses import dataclass
import datetime
import logging
from typing import Coroutine, Iterable
import numpy as np
from sqlalchemy.orm import Session

from app.adapter.visual_crossing_adapter import GetWeatherRequest, visual_crossing_adapter
from app.api.request.get_summary_request import GetWeatherSummaryRequest
from app.api.request.get_weather_detail_request import GetWeatherDetailRequest
from app.common.constant import SUCCESS_STATUS_CODE
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


async def get_map_date_to_weather_log(ctx: Context, model: Nb2MosquittoModel, location: Location, list_time: list[int]) -> dict[int, WeatherLog]:
    db_session = ctx.extract_db_session()
    resp: dict[int, WeatherLog] = {}
    for time in list_time:
        query = db_session.query(WeatherLog).where(
            WeatherLog.location_id == location.id, WeatherLog.date_time == time)
        weather_log = query.first()
        if weather_log is None:
            # if we cannot get this weather log we will try to call to visual crossing to get weather
            req = GetWeatherRequest(
                longitude=location.longitude,
                latitude=location.latitude,
                start_date_time=time_util.to_start_date_timestamp(time),
                end_date_time=time_util.to_end_date_timestamp(time),
            )
            weather_log_resp = visual_crossing_adapter.get_weather_log(req)
            if weather_log_resp.code != SUCCESS_STATUS_CODE:
                raise ThirdServiceException()
            data = weather_log_resp.data[0]
            # save it without time window id, will have celery job to update it later
            weather_log = WeatherLog(**data.dict(), location_id=location.id)
            weather_log_repo.save(db_session, weather_log)
        resp.update({time: weather_log})
    return resp


async def get_map_date_to_prediction(
        ctx: Context, model: Nb2MosquittoModel, location_id: int, list_time: list[int]) -> dict[
        int, float]:
    resp: dict[int, float] = {}
    db_session = ctx.extract_db_session()
    for time in list_time:
        prediction = model.predict_with_location_id(
            location_id=location_id, date_time=time, db_session=db_session)
        resp.update({time: prediction.count})
    return resp


async def get_weather_detail(ctx: Context, model: Nb2MosquittoModel,
                             request: GetWeatherDetailRequest) -> WeatherDetailDTO:
    logger = ctx.extract_logger()
    db_session = ctx.extract_db_session()

    internal_location, third_party_location = _find_location_by_long_lat(
        ctx, RequestLocation(lat=request.lat, long=request.lng))
    start_time_dt = time_util.ts_to_datetime(request.start_time)
    time_interval = time_util.ts_to_datetime(request.end_time) - start_time_dt
    list_time = [time_util.datetime_to_ts(start_time_dt+datetime.timedelta(i)) for i in range(time_interval.days)]
    map_date_to_prediction = await get_map_date_to_prediction(
        ctx, model, location_id=internal_location.id, list_time=list_time)
    map_date_to_weather_log = await get_map_date_to_weather_log(
        ctx, model, location=internal_location, list_time=list_time)

    return WeatherDetailDTO(
        lat=request.lat,
        long=request.lng,
        location_code=third_party_location.location_code,
        map_date_to_prediction_value=map_date_to_prediction,
        map_date_to_weather_log=map_date_to_weather_log,
    )
