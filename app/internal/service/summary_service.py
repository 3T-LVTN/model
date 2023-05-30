

import asyncio
from dataclasses import dataclass
import datetime
import json
import logging
from typing import Coroutine, Iterable
import numpy as np
from sqlalchemy.orm import Session

from app.api.request.get_summary_request import GetWeatherSummaryRequest
from app.api.request.get_weather_detail_request import GetWeatherDetailRequest
from app.common.context import Context
from app.api.request.get_summary_request import Location as RequestLocation
from app.internal.model.model.model import Nb2MosquittoModel
from app.internal.service.common import _find_location_by_long_lat, get_map_location_by_location_support_filter, get_weather_log_with_location_ids, predict_with_location_ids, get_map_date_to_prediction, get_map_date_to_weather_log
from app.internal.service.dto.weather_detail_dto import WeatherDetailDTO
from app.internal.service.dto.weather_summary_dto import WeatherSummaryDTO
from app.internal.util.time_util import time_util


async def get_weather_summary(ctx: Context, model: Nb2MosquittoModel, request: GetWeatherSummaryRequest) -> WeatherSummaryDTO:

    map_location_id_to_location, map_location_id_to_third_party = await get_map_location_by_location_support_filter(
        ctx, request.locations)

    # create tasks
    predict_task = asyncio.create_task(
        predict_with_location_ids(
            ctx=ctx, model=model, location_ids=map_location_id_to_location.keys(),
            time=time_util.datetime_to_ts(time_util.now())))

    weather_task = asyncio.create_task(get_weather_log_with_location_ids(ctx, map_location_id_to_location.keys()))
    # wait for tasks
    await predict_task
    await weather_task
    # achieve result
    map_location_id_to_prediction, map_location_to_quartile = predict_task.result()
    map_location_id_to_weather_log = weather_task.result()

    return WeatherSummaryDTO(
        map_location_id_to_weather_log=map_location_id_to_weather_log,
        map_location_id_to_prediction=map_location_id_to_prediction,
        map_location_id_to_third_party=map_location_id_to_third_party,
        map_location_id_to_location=map_location_id_to_location,
        map_location_id_to_quartile=map_location_to_quartile
    )


async def get_weather_detail(ctx: Context, model: Nb2MosquittoModel,
                             request: GetWeatherDetailRequest) -> WeatherDetailDTO:

    location_task = asyncio.create_task(_find_location_by_long_lat(
        ctx, RequestLocation(lat=request.lat, long=request.lng)))
    start_time_dt = time_util.ts_to_datetime(request.start_time)
    time_interval = time_util.ts_to_datetime(request.end_time) - start_time_dt
    list_time = [time_util.datetime_to_ts(start_time_dt+datetime.timedelta(i)) for i in range(time_interval.days)]

    await location_task
    internal_location, third_party_location = location_task.result()

    predict_task = asyncio.create_task(get_map_date_to_prediction(
        ctx, model, location_id=internal_location.id, list_time=list_time))
    weather_log_task = asyncio.create_task(get_map_date_to_weather_log(
        ctx, model, location=internal_location, list_time=list_time))

    await predict_task
    await weather_log_task

    map_date_to_prediction, map_date_to_quartile = predict_task.result()
    map_date_to_weather_log = weather_log_task.result()

    return WeatherDetailDTO(
        lat=request.lat,
        long=request.lng,
        location_code=third_party_location.location_code,
        map_date_to_prediction_value=map_date_to_prediction,
        map_date_to_weather_log=map_date_to_weather_log,
        map_date_to_quartile=map_date_to_quartile,
    )
