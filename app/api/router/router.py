from fastapi.routing import APIRoute
from fastapi import APIRouter

from app.middleware.router.router import CustomAPIRouter
from app.api.router.prediction_router import prediction_router
from app.api.router.file_router import file_router

router = CustomAPIRouter()
router.include_router(prediction_router)
router.include_router(file_router)
