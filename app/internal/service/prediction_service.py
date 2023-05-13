
from dataclasses import dataclass
import datetime
import logging
import numpy as np

from app.api.request.get_prediction_request import GetPredictionRequest
from app.common.context import Context
from app.common.exception import ThirdServiceException
from app.internal.model.model.model import Nb2MosquittoModel
from app.internal.service.dto.prediction_dto import PredictionDTO


def get_prediction(ctx: Context, model: Nb2MosquittoModel, request: GetPredictionRequest) -> dict[int, PredictionDTO]:
    db_session = ctx.extract_db_session()
    result: list[PredictionDTO] = []
    for location in request.locations:
        try:
            prediction = model.predict(longitude=location.long, latitude=location.lat,
                                       date_time=request.predictDate, db_session=db_session)
        except ThirdServiceException:
            logging.info("third party has no data for this locations")
            continue
        if prediction is not None and not np.isinf(prediction.count):
            result.append(PredictionDTO(idx=location.idx, weight=prediction.count))
        else:
            result.append(PredictionDTO(idx=location.idx))
    return {x.idx: x for x in map(lambda x: PredictionDTO(idx=x.idx, weight=x.weight), result)}
