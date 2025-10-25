from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.api.v1.services.country_service import CountryService
from app.api.v1.schemas.status import StatusResponse

router = APIRouter()

@router.get("/status", response_model=StatusResponse)
def get_status(
    db: Session = Depends(get_db)
):
    """
    Get database status showing:
    - total_countries: Total number of countries in the database
    - last_refreshed_at: Timestamp of last refresh
    
    Example Response:
    {
        "total_countries": 250,
        "last_refreshed_at": "2025-10-22T18:00:00Z"
    }
    """
    service = CountryService(db)
    status = service.get_status()
    return status