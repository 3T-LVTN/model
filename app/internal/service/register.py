from abc import abstractmethod
from typing import Protocol
from sqlalchemy.orm import Session

from app.api.request.get_prediction_request import GetPredictionRequest
from app.api.response.get_prediction_response import GetPredictionResponse
from app.common.context import Context
from app.config import env_var
from app.internal.model.model.model import Nb2MosquittoModel
from app.internal.service.prediction_service import get_prediction
from app.internal.service.transformer.prediction_transformer import PredictionTransformer


class IService(Protocol):
    @abstractmethod
    def get_prediction(self, ctx: Context,  request: GetPredictionRequest): ...


class Service(IService):

    def __init__(self) -> None:
        if env_var.IS_EXPERIMENT:
            # load list of available model
            return
        # if not experiment init first models
        self.models = [Nb2MosquittoModel(1)]
        self.transformer = PredictionTransformer()

    def get_prediction(self, ctx: Context,  request: GetPredictionRequest) -> GetPredictionResponse:
        data = get_prediction(ctx, self.models[0], request)
        return self.transformer.prediction_dto_to_response(request, data)


service = Service()
