import concurrent.futures as ft
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
from app.internal.dao.predicted_log import PredictedLog
from app.internal.dao.prediction_quartile import PredictionQuartile
from app.internal.dao.third_party_location import ThirdPartyLocation
from app.internal.dao.weather_log import WeatherLog
from app.internal.model.model.model import Nb2MosquittoModel
from app.internal.repository.location import LocationFilter, location_repo
from app.internal.repository.weather_log import WeatherLogFilter, weather_log_repo
from app.internal.repository.third_party_location import third_party_location_repo, ThirdPartyLocationFilter
from app.internal.util.time_util import time_util


def get_map_date_to_quartile(ctx: Context, prediction: float, time: int) -> int:
    db_session = ctx.extract_db_session()
    time = time_util.to_start_date_timestamp(time)
    quartile = db_session.query(PredictionQuartile).where(PredictionQuartile.time == time).first()
    quartile_threshold = []
    if quartile is not None:
        quartile_threshold = quartile.quartile_threshold
    else:
        pred_log = db_session.query(PredictedLog).where(PredictedLog.predict_time == time).all()
        if len(pred_log) > 0:
            log_values = [log.value for log in pred_log]
            quartile_threshold = np.quantile(log_values, [0.25, 0.5, 0.75]).tolist()
            db_session.add(PredictionQuartile(
                time=time,
                quartile_threshold=quartile_threshold
            ))
    for idx, thrs in enumerate(quartile_threshold):
        if prediction < thrs:
            return idx
    return len(quartile_threshold) - 1


class LocationFilterSupported(Protocol):
    lat: float
    lng: float
    location_code: str = None


def _find_location_by_long_lat(ctx: Context, location_request: LocationFilterSupported) -> tuple[Location,
                                                                                                 ThirdPartyLocation]:
    logging.info(location_request.lat)
    logging.info(location_request.lng)
    db_session = ctx.extract_db_session()
    if location_request.lat is None or location_request.lng is None:
        return None, None
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


def predict_with_location_ids(ctx: Context, model: Nb2MosquittoModel, location_ids: Iterable[int],
                              time: int) -> tuple[dict[int, float],
                                                  dict[int, int]]:
    db_session = ctx.extract_db_session()
    # define share resource
    map_location_id_to_prediction: dict[int, float] = {}
    map_location_id_to_quarttile: dict[int, int] = {}

    with ft.ThreadPoolExecutor() as pool:
        ft_pool = {
            pool.submit(
                model.predict_with_location_id, db_session=db_session, location_id=location, date_time=time): location
            for location in location_ids}
        for future in ft.as_completed(ft_pool.keys()):
            location = ft_pool.get(future)
            prediction = future.result()
            map_location_id_to_prediction.update({location: prediction.count})
            map_location_id_to_quarttile.update({
                location:  get_map_date_to_quartile(ctx, prediction.count, time)
            })

    return map_location_id_to_prediction, map_location_id_to_quarttile


def get_weather_log_with_location_ids(ctx: Context, location_ids: Iterable[int]) -> dict[int, WeatherLog]:
    db_session = ctx.extract_db_session()
    weather_logs = weather_log_repo.filter_all(db_session=db_session, filter=WeatherLogFilter(
        location_ids=location_ids
    ))
    map_location_id_to_weather_log = {log.location_id: log for log in weather_logs}
    return map_location_id_to_weather_log


def get_map_location_by_location_support_filter(
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
            internal_location, third_party_location = _find_location_by_long_lat(ctx, location)
            if internal_location is None or third_party_location is None:
                continue
            map_location_id_to_third_party.update({internal_location.id: third_party_location})
            map_location_id_to_location.update({internal_location.id: internal_location})

    return map_location_id_to_location, map_location_id_to_third_party


def get_prediction_for_date(ctx: Context, model: Nb2MosquittoModel, location_id: int, date: int) -> float:
    db_session = ctx.extract_db_session()
    prediction = model.predict_with_location_id(location_id=location_id, date_time=date, db_session=db_session)
    return prediction.count


def get_map_date_to_weather_log(
        ctx: Context, model: Nb2MosquittoModel, location: Location, list_time: list[int]) -> dict[
        int, WeatherLog]:
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


def get_map_date_to_prediction(
        ctx: Context, model: Nb2MosquittoModel, location_id: int, list_time: list[int]) -> tuple[dict[
        int, float], dict[int, int]]:
    map_time_to_pred: dict[int, float] = {}
    map_time_to_quartile: dict[int, int] = {}
    db_session = ctx.extract_db_session()

    # define task
    for time in list_time:
        prediction = model.predict_with_location_id(
            location_id=location_id, date_time=time, db_session=db_session)
        map_time_to_pred.update({time: prediction.count})
        map_time_to_quartile.update({time: get_map_date_to_quartile(ctx, prediction.count, time)})
    return map_time_to_pred, map_time_to_quartile
