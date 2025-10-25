from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.api.v1.services.refresh_service import RefreshService

router = APIRouter()

@router.post("/countries/refresh")
async def refresh_countries(
    db: Session = Depends(get_db)
):
    """
    Fetch all countries and exchange rates from external APIs,
    then cache them in the database.
    
    Process:
    1. Fetch countries from restcountries.com
    2. Fetch exchange rates from open.er-api.com
    3. Match currencies and calculate GDP
    4. Update/Insert into database
    5. Generate summary image
    
    Returns:
    - message: Success message
    - countries_processed: Number of countries processed
    - total_countries: Total countries in database
    - last_refreshed_at: Timestamp of refresh
    
    Raises:
    - 503: External API unavailable
    - 500: Internal server error
    """
    service = RefreshService(db)
    result = await service.refresh_countries()
    return result