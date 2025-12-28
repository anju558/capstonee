from fastapi import APIRouter

from .auth_routes import router as auth_router
from .events_routes import router as events_router
from .analytics_routes import router as analytics_router
router.include_router(analysis_router)

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(events_router, prefix="/events", tags=["Events"])
router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
