from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.roadmaps import router as roadmaps_router, node_router
from app.routers.ai import router as ai_router

__all__ = [
    "auth_router",
    "users_router",
    "roadmaps_router",
    "node_router",
    "ai_router",
]
