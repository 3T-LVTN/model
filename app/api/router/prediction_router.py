from sqlalchemy.orm import Session

from app.middleware.router.router import CustomAPIRouter
from app.api.response.get_prediction_response import GetPredictionResponse
from app.api.request.get_prediction_request import GetPredictionRequest
from app.internal.service.register import service
from app.common.context import Context

prediction_router = CustomAPIRouter()


@prediction_router.post("v1/prediction", response_model=GetPredictionResponse)
def get_prediction(ctx: Context, request: GetPredictionRequest):
    ctx.extract_logger("API", "prediction")
    return service.get_prediction(ctx, request)
