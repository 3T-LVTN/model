from app.middleware.router.router import CustomAPIRouter
from app.api.router.prediction_router import prediction_router

router = CustomAPIRouter()
router.prefix = "/api/v1"
router.include_router(prediction_router, prefix="router")
