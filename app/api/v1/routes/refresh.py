from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.api.v1.services.refresh_service import RefreshService
from app.utils.exceptions import ExternalAPIException

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
    """
    service = RefreshService(db)
    
    try:
        result = await service.refresh_countries()
        return result
    except ExternalAPIException as e:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "External data source unavailable",
                "details": f"Could not fetch data from {e.api_name}"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error"}
        )