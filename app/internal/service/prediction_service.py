
from dataclasses import dataclass
import datetime
import numpy as np

from app.api.request.get_prediction_request import GetPredictionRequest
from app.common.context import Context
from app.internal.model.model.model import Nb2MosquittoModel
from app.internal.service.dto.prediction_dto import PredictionDTO


def get_prediction(ctx: Context, model: Nb2MosquittoModel, request: GetPredictionRequest) -> dict[int, PredictionDTO]:
    db_session = ctx.extract_db_session()
    result: list[PredictionDTO] = []
    max_value = -np.Infinity
    for location in request.locations:
        prediction = model.predict(longitude=location.long, lattitude=location.lat,
                                   date_time=int(datetime.datetime.now().timestamp()), db_session=db_session)
        if prediction is not None and not np.isinf(prediction.count):
            max_value = np.max([max_value, prediction.count])
            result.append(PredictionDTO(idx=location.idx, weight=prediction.count))
        else:
            result.append(PredictionDTO(idx=location.idx))
    return {x.idx: x for x in map(lambda x: PredictionDTO(idx=x.idx, weight=None if x is x.weight is None else x.weight/max_value), result)}
