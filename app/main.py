from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import (
    auth_router, collection_router, disease_router,
    restoration_router, patrol_router, image_router, transfer_router
)
from app.api.export import router as export_router
from app.api.scan import router as scan_router
from app import init_db

init_db()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(collection_router, prefix=settings.API_V1_STR)
app.include_router(disease_router, prefix=settings.API_V1_STR)
app.include_router(restoration_router, prefix=settings.API_V1_STR)
app.include_router(patrol_router, prefix=settings.API_V1_STR)
app.include_router(image_router, prefix=settings.API_V1_STR)
app.include_router(transfer_router, prefix=settings.API_V1_STR)
app.include_router(export_router, prefix=settings.API_V1_STR)
app.include_router(scan_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} - API服务运行中"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}