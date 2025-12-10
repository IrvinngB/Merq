from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import (
    auth_router,
    users_router,
    roadmaps_router,
    node_router,
    ai_router,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Plataforma de roadmaps educativos con IA",
    version=settings.VERSION,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(roadmaps_router)
app.include_router(node_router)
app.include_router(ai_router)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Merq API is running"}
