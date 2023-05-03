import logging
import uuid
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.internal.dao import db

from app.middleware.router.router import CustomAPIRouter
from app.api.response.base import BaseResponse
from app.api.request.get_prediction_request import GetPredictionRequest
from app.adapter.file_service.file_service_adapter import file_service
from app.common.context import Context, get_context
from app.internal.util.time_util import time_util
from app.common.exception import ThirdServiceException
from fastapi import FastAPI, File, UploadFile
from botocore.exceptions import ClientError


file_router = CustomAPIRouter()


@file_router.post("/upload", response_model=BaseResponse)
async def create_upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()

        file_service_file_name = f"{file.filename}_{time_util.datetime_to_file_name_str(time_util.now())}_{str(uuid.uuid4())}"
        content = bytes(content, encoding='utf-8') if isinstance(content, str) else content
        file_service.upload_file(content=content, file_name=file_service_file_name)
    except ClientError as e:
        logging.info(f"file service error: {e}")
        raise ThirdServiceException()

    return BaseResponse()
