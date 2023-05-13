import logging
import uuid
from sqlalchemy.orm import Session
from fastapi import FastAPI, File, UploadFile, Depends
from botocore.exceptions import ClientError

from app.internal.dao import db
from app.internal.dao.synced_file import SyncedFile
from app.middleware.router.router import CustomAPIRouter
from app.api.response.base import BaseResponse
from app.api.request.get_prediction_request import GetPredictionRequest
from app.adapter.file_service import file_service_adapter
from app.common.context import Context, get_context
from app.internal.util.time_util import time_util
from app.common.exception import ThirdServiceException
from app.internal.repository.synced_file import synced_file_repo
from app.internal.dao.db import get_db_session


file_router = CustomAPIRouter()


@file_router.post("/upload", response_model=BaseResponse)
async def create_upload_file(file: UploadFile = File(...), db_session: Session = Depends(get_db_session)):
    try:
        content = await file.read()

        file_service_file_name = f"{file.filename}_{time_util.datetime_to_file_name_str(time_util.now())}_{str(uuid.uuid4())}"
        synced_file_repo.save(db_session, SyncedFile(file_name=file_service_file_name))
        content = bytes(content, encoding='utf-8') if isinstance(content, str) else content
        file_service_adapter.file_service.upload_file(content=content, file_name=file_service_file_name)
    except ClientError as e:
        logging.info(f"file service error: {e}")
        raise ThirdServiceException()
    return BaseResponse()
