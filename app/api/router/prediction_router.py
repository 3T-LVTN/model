from http import HTTPStatus
import logging
import uuid
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from botocore.exceptions import ClientError

from app.adapter.file_service import file_service_adapter
from app.api.response.base import BaseResponse
from app.common.constant import ALLOW_FILE_EXTENSION
from app.common.exception import ThirdServiceException
from app.internal.dao import db
from app.internal.dao.synced_file import SyncedFile
from app.internal.repository.synced_file import synced_file_repo
from app.internal.service.register import service
from app.internal.util.time_util import time_util
from app.middleware.router.router import CustomAPIRouter
from app.api.response.get_prediction_response import GetPredictionResponse
from app.api.request.get_prediction_request import GetPredictionRequest
from app.api.request.get_weather_detail_request import GetWeatherDetailRequest
from app.api.response.get_weather_detail_response import GetWeatherDetailResponse
from app.api.request.get_summary_request import GetWeatherSummaryRequest
from app.api.response.get_summary_response import GetHCMCProviceSummaryResponse, GetWeatherSummaryResponse
from app.common.context import Context, get_context

prediction_router = CustomAPIRouter()


@prediction_router.post("/prediction", response_model=GetPredictionResponse)
def get_prediction(
        request: GetPredictionRequest, db_session: Session = Depends(db.get_db_session),
        ctx: Context = Depends(get_context)):
    try:
        logging.info("api prediction")
        ctx.attach_db_session(db_session)
        return service.get_prediction(ctx, request)
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.commit()


@prediction_router.post("/prediction/summary", response_model=GetWeatherSummaryResponse)
def get_weather_summary(
        request: GetWeatherSummaryRequest, db_session: Session = Depends(db.get_db_session),
        ctx: Context = Depends(get_context)):
    try:
        logging.info("api prediction summary")
        ctx.attach_db_session(db_session)
        return service.get_weather_summary(ctx, request)
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.commit()


@prediction_router.post("/prediction/detail", response_model=GetWeatherDetailResponse)
def get_weather_detail(request: GetWeatherDetailRequest, db_session: Session = Depends(
        db.get_db_session), ctx: Context = Depends(get_context)):
    try:
        logging.info("api prediction detail")
        ctx.attach_db_session(db_session)
        return service.get_weather_detail(ctx, request)
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.commit()


@prediction_router.post("/prediction/upload/", response_model=BaseResponse)
async def create_upload_file(file: UploadFile = File(...), db_session: Session = Depends(db.get_db_session)):
    logging.info("api upload file")
    try:
        content = await file.read()
        file_name = file.filename.replace(" ", "_")
        file_extension = file_name[file_name.rfind(".")+1:]
        if not file_extension in ALLOW_FILE_EXTENSION:
            raise HTTPException(HTTPStatus.BAD_REQUEST.value, detail="not allow file type")
        file_name = file_name[:file_name.rfind(".")]
        file_service_file_name = f"{file.filename}_{time_util.datetime_to_file_name_str(time_util.now())}_{str(uuid.uuid4())}.{file_extension}"

        synced_file_repo.save(db_session, SyncedFile(file_name=file_service_file_name))
        content = bytes(content, encoding='utf-8') if isinstance(content, str) else content
        file_service_adapter.file_service.upload_file(content=content, file_name=file_service_file_name)
    except ClientError as e:
        logging.info(f"file service error: {e}")
        raise ThirdServiceException()
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.commit()
    return BaseResponse()


@prediction_router.get("/prediction/summary/hcmc")
def get_hcmc_summary(db_session: Session = Depends(db.get_db_session), ctx: Context = Depends(get_context)):
    try:
        ctx.attach_db_session(db_session)
        return service.get_hcmc_summary(ctx).dict()
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.commit()
