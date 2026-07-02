from app.api.auth import router as auth_router
from app.api.collection import router as collection_router
from app.api.disease import router as disease_router
from app.api.restoration import router as restoration_router
from app.api.patrol import router as patrol_router
from app.api.image import router as image_router
from app.api.transfer import router as transfer_router

__all__ = [
    "auth_router",
    "collection_router",
    "disease_router",
    "restoration_router",
    "patrol_router",
    "image_router",
    "transfer_router"
]