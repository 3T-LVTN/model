from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.internal.dao import db

from app.internal.service.register import service
from app.middleware.router.router import CustomAPIRouter
from app.api.response.get_prediction_response import GetPredictionResponse
from app.api.request.get_prediction_request import GetPredictionRequest
from app.api.request.get_weather_detail_request import GetWeatherDetailRequest
from app.api.response.get_weather_detail_response import GetWeatherDetailResponse
from app.api.request.get_summary_request import GetWeatherSummaryRequest
from app.api.response.get_summary_response import GetWeatherSummaryResponse
from app.common.context import Context, get_context

prediction_router = CustomAPIRouter()


@prediction_router.post("/prediction", response_model=GetPredictionResponse)
def get_prediction(
        request: GetPredictionRequest, db_session: Session = Depends(db.get_db_session),
        ctx: Context = Depends(get_context)):

    ctx.extract_logger("API", "prediction")
    ctx.attach_db_session(db_session)
    return service.get_prediction(ctx, request)


@prediction_router.post("/weather_log/summary", response_model=GetWeatherSummaryResponse)
def get_weather_summary(
        request: GetWeatherDetailRequest, db_session: Session = Depends(db.get_db_session),
        ctx: Context = Depends(get_context)):
    ctx.extract_logger("API", "weather_log summary")
    ctx.attach_db_session(db_session)
    return service.get_weather_summary(ctx, request)


@prediction_router.post("/weather_log/detail", response_model=GetWeatherDetailResponse)
def get_weather_detail(request: GetWeatherDetailRequest, db_session: Session = Depends(
    db.get_db_session), ctx: Context = Depends(get_context)):
    ctx.extract_logger("API", "weather_log detail")
    ctx.attach_db_session(db_session)
    return service.get_weather_detail(ctx, request)
