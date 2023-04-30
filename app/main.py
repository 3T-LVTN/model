import logging
import logging.config
import sys
import uvicorn

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

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

    # add middleware to set context
    app.add_middleware(CustomContextMiddleware)
    app.include_router(router, prefix="/api")

    # Add exception handler
    # add known exception handler in future
    # application.add_exception_handler(DefinedException, defined_exception_handler)

    # add request validation error in future
    # application.add_exception_handler(
    #     RequestValidationError, validation_exception_handler
    # )
    return app


app = get_application()


@app.on_event("startup")
async def startup_event():

    # Set log level
    logging.basicConfig(level=logging.INFO)
    # from app.internal.service.register import service  # initialize service to ensure model is load


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False)
