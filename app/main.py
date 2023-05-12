import logging
import logging.config
import sys
import uvicorn

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.adapter.base import BaseResponse
from app.common.exception import ThirdServiceException
from app.config import env_var
from app.middleware.context_middleware import CustomContextMiddleware
from app.internal.celery.celery import celery_app  # noqa #import this so we can start celery when we start app
from app.api.router.router import router
from app.internal.model.model.model import Nb2MosquittoModel

logging.StreamHandler(sys.stdout)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.config.dictConfig(env_var.LOGGING_CONFIG)


def get_application() -> FastAPI:
    app = FastAPI(docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # add middleware to set context
    app.add_middleware(CustomContextMiddleware)
    app.include_router(router, prefix="/api")

    # Add exception handler
    # add known exception handler in future
    app.add_exception_handler(ThirdServiceException, lambda request, e:  JSONResponse(
        status_code=500,
        content=BaseResponse(code=e.code, message="another third party service, retry later or choose another location"))
    )

    # add request validation error in future
    # application.add_exception_handler(
    #     RequestValidationError, validation_exception_handler
    # )
    return app


app = get_application()


@ app.on_event("startup")
async def startup_event():
    import os
    os.system('alembic upgrade head')
    # Set log level
    logging.basicConfig(level=logging.INFO)
    # from app.internal.service.register import service  # initialize service to ensure model is load


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False)
