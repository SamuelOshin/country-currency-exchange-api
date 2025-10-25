from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.api.v1.services.image_service import ImageService

router = APIRouter()

@router.get("/countries/image")
def get_summary_image():
    """
    Serve the generated summary image showing:
    - Total number of countries
    - Top 5 countries by estimated GDP
    - Timestamp of last refresh
    
    The image is generated during POST /countries/refresh
    
    Returns: PNG image file
    Raises: 404 if image doesn't exist
    """
    if not ImageService.image_exists():
        raise HTTPException(
            status_code=404,
            detail={"error": "Summary image not found"}
        )
    
    image_path = ImageService.get_image_path()
    return FileResponse(
        image_path,
        media_type="image/png",
        filename="summary.png"
    )