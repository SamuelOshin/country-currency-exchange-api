from fastapi import APIRouter
from app.api.v1.routes import countries, refresh, status, image

# Create main v1 router
router = APIRouter()

# Include all route modules
router.include_router(image.router, tags=["image"])
router.include_router(refresh.router, tags=["refresh"])
router.include_router(status.router, tags=["status"])
router.include_router(countries.router, tags=["countries"])