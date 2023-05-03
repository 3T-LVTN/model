from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.internal.dao import db

from app.middleware.router.router import CustomAPIRouter
from app.api.response.get_prediction_response import GetPredictionResponse
from app.api.request.get_prediction_request import GetPredictionRequest
from app.common.context import Context, get_context

prediction_router = CustomAPIRouter()


@prediction_router.post("/prediction", response_model=GetPredictionResponse)
async def get_prediction(
        request: GetPredictionRequest, db_session: Session = Depends(db.get_db_session),
        ctx: Context = Depends(get_context)):
    from app.internal.service.register import service

    ctx.extract_logger("API", "prediction")
    ctx.attach_db_session(db_session)
    return service.get_prediction(ctx, request)
