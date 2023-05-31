
import asyncio
from dataclasses import dataclass
import datetime
import logging
import numpy as np

from app.api.request.get_prediction_request import GetPredictionRequest
from app.common.context import Context
from app.common.exception import ThirdServiceException
from app.internal.dao.location import Location
from app.internal.model.model.model import Nb2MosquittoModel
from app.internal.repository.third_party_location import ThirdPartyLocationFilter, third_party_location_repo
from app.internal.service.common import get_map_location_by_location_support_filter
from app.internal.service.dto.prediction_dto import PredictionDTO


async def get_prediction(ctx: Context, model: Nb2MosquittoModel, request: GetPredictionRequest) -> dict[int, float]:
    '''return location map id to prediction'''
    db_session = ctx.extract_db_session()
    result: dict[int, float] = {}
    map_location, _ = await get_map_location_by_location_support_filter(ctx, request.locations)

    # define task

    async def get_pred(location_id: int, location: Location):
        try:
            prediction = model.predict_with_location_id(
                location_id=location_id, date_time=request.predict_date, db_session=db_session)
            logging.info(f"prediction: {prediction.count}")
        except ThirdServiceException:
            logging.info("third party has no data for this locations")
            return
        if prediction is not None and not np.isinf(prediction.count):
            result.update({location.id: prediction.count})

    task_group = [asyncio.create_task(get_pred(location_id, location))
                  for location_id, location in map_location.items()]

    await asyncio.wait(task_group)

    return result
