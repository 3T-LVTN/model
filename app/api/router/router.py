from fastapi.routing import APIRoute
from fastapi import APIRouter

from app.middleware.router.router import CustomAPIRouter
from app.api.router.prediction_router import prediction_router

router = APIRouter()
router.include_router(prediction_router)
