from dataclasses import dataclass
import datetime
import logging
from typing import Coroutine, Iterable, Protocol, Sequence
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


class LocationFilterSupported(Protocol):
    lat: float
    lng: float
    location_code: str = None


async def _find_location_by_long_lat(ctx: Context, location_request: LocationFilterSupported) -> tuple[Location,
                                                                                                       ThirdPartyLocation]:
    db_session = ctx.extract_db_session()

    # find the location we are currently refer to
    location = location_repo.get_first(db_session=db_session, filter=LocationFilter(
        longitude=location_request.lng,
        latitude=location_request.lat
    ))
    # if this is new location create new record in db
    if location is None:
        location = Location(
            longitude=location_request.lng,
            latitude=location_request.lat,
        )
        db_session.add(location)
    # cache this location code
    third_party_location = ThirdPartyLocation(
        location_code=location_request.location_code,
        location_id=location.id
    )
    db_session.add(third_party_location)
    db_session.flush()
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


async def get_map_location_by_location_support_filter(
        ctx: Context, inp: Sequence[LocationFilterSupported]) -> tuple[
        dict[int, Location],
        dict[int, ThirdPartyLocation]]:
    db_session = ctx.extract_db_session()
    location_codes = [location.location_code for location in inp if location.location_code is not None]
    if len(location_codes) > 0:
        third_party_locations = third_party_location_repo.filter_all(db_session, ThirdPartyLocationFilter(
            location_codes=location_codes
        ))
    else:
        third_party_locations = []
    map_location_id_to_third_party = {location.location_id: location for location in third_party_locations}
    map_location_id_to_location = {location.location.id: location.location for location in third_party_locations}
    location_codes = [location.location_code for location in third_party_locations]
    for location in inp:
        if location.location_code not in location_codes:
            internal_location, third_party_location = await _find_location_by_long_lat(ctx, location)
            map_location_id_to_third_party.update({internal_location.id: third_party_location})
            map_location_id_to_location.update({internal_location.id: internal_location})

    return map_location_id_to_location, map_location_id_to_third_party
