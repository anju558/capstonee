from fastapi import APIRouter

from backend.routes.auth_routes import router as auth_router
from backend.routes.skill_analysis import router as skill_router
from backend.routes.analytics_routes import router as analytics_router
from backend.routes.events_routes import router as events_router
from backend.routes.rag import router as rag_router
from backend.routes.knowledge_routes import router as knowledge_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth")
router.include_router(skill_router)
router.include_router(analytics_router)
router.include_router(events_router)
router.include_router(rag_router)
router.include_router(knowledge_router)
