

import concurrent.futures as ft
from dataclasses import dataclass
import datetime
import json
import logging
from typing import Coroutine, Iterable, Optional, Sequence
import numpy as np
from sqlalchemy.orm import Session

from app.api.request.get_summary_request import GetWeatherSummaryRequest
from app.api.request.get_weather_detail_request import GetWeatherDetailRequest
from app.common.context import Context
from app.api.request.get_summary_request import Location as RequestLocation
from app.internal.dao.location import Location
from app.internal.dao.third_party_location import ThirdPartyLocation
from app.internal.dao.weather_log import WeatherLog
from app.internal.model.model.model import Nb2MosquittoModel
from app.internal.repository.third_party_location import ThirdPartyLocationFilter, third_party_location_repo
from app.internal.service.common import _find_location_by_long_lat, get_map_location_by_location_support_filter, get_weather_log_with_location_ids, predict_with_location_ids, get_map_date_to_prediction, get_map_date_to_weather_log
from app.internal.service.dto.weather_detail_dto import WeatherDetailDTO
from app.internal.service.dto.weather_summary_dto import WeatherSummaryDTO
from app.internal.util.time_util import time_util


def get_weather_summary(ctx: Context, model: Nb2MosquittoModel, request: GetWeatherSummaryRequest) -> WeatherSummaryDTO:
    map_location_id_to_location: dict[int, Location] = {}
    map_location_id_to_third_party: dict[int, ThirdPartyLocation] = {}
    map_idx_to_location_id: dict[int, int] = {}
    for inp in request.locations:
        location, third_party_location = _find_location_by_long_lat(ctx, inp)
        map_location_id_to_location.update({location.id: location})
        map_location_id_to_third_party.update({location.id: third_party_location})
        map_idx_to_location_id.update({inp.idx: location.id})

    map_location_id_to_prediction: dict[int, float] = {}
    map_location_to_quartile: dict[int, int] = {}
    map_location_id_to_weather_log: dict[int, WeatherLog] = {}
    # create tasks

    map_location_id_to_prediction, map_location_to_quartile = predict_with_location_ids(
        ctx=ctx, model=model, location_ids=map_location_id_to_location.keys(),
        time=time_util.datetime_to_ts(time_util.now()))

    map_location_id_to_weather_log = get_weather_log_with_location_ids(ctx, map_location_id_to_location.keys())

    return WeatherSummaryDTO(
        map_location_id_to_weather_log=map_location_id_to_weather_log,
        map_location_id_to_prediction=map_location_id_to_prediction,
        map_location_id_to_third_party=map_location_id_to_third_party,
        map_location_id_to_location=map_location_id_to_location,
        map_location_id_to_quartile=map_location_to_quartile,
        map_idx_to_location_id=map_idx_to_location_id
    )


def get_weather_detail(ctx: Context, model: Nb2MosquittoModel,
                       request: GetWeatherDetailRequest) -> Optional[WeatherDetailDTO]:
    db_session = ctx.extract_db_session()
    logging.info(request.json())
    third_party_location = None
    if request.location_code is not None:
        third_party_location_page = third_party_location_repo.filter(db_session, ThirdPartyLocationFilter(
            location_codes=[request.location_code]
        ))
        if len(third_party_location_page.content) != 0:
            third_party_location = third_party_location_page.content[0]
            internal_location = third_party_location.location
    if third_party_location is None:
        internal_location, third_party_location = _find_location_by_long_lat(
            ctx, RequestLocation(lat=request.lat, lng=request.lng))

    start_time_dt = time_util.ts_to_datetime(request.start_time)
    time_interval = time_util.ts_to_datetime(request.end_time) - start_time_dt
    list_time = [time_util.datetime_to_ts(start_time_dt+datetime.timedelta(i)) for i in range(time_interval.days)]

    map_date_to_prediction: dict[int, float] = {}
    map_date_to_quartile: dict[int, int] = {}
    map_date_to_weather_log: dict[int, WeatherLog] = {}

    map_date_to_prediction, map_date_to_quartile = get_map_date_to_prediction(
        ctx, model, location_id=internal_location.id, list_time=list_time)

    map_date_to_weather_log = get_map_date_to_weather_log(
        ctx, model, internal_location, list_time)

    return WeatherDetailDTO(
        lat=request.lat,
        long=request.lng,
        location_code=third_party_location.location_code,
        map_date_to_prediction_value=map_date_to_prediction,
        map_date_to_weather_log=map_date_to_weather_log,
        map_date_to_quartile=map_date_to_quartile,
    )
