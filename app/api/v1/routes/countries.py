from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.dependencies import get_db
from app.api.v1.services.country_service import CountryService
from app.api.v1.schemas.country import CountryResponse

router = APIRouter()

@router.get("/countries", response_model=List[CountryResponse])
def get_countries(
    region: Optional[str] = Query(None, description="Filter by region (e.g., Africa)"),
    currency: Optional[str] = Query(None, description="Filter by currency code (e.g., NGN)"),
    sort: Optional[str] = Query(None, description="Sort order (gdp_desc, gdp_asc, name_asc, name_desc)"),
    db: Session = Depends(get_db)
):
    """
    Get all countries with optional filters and sorting
    
    Filters:
    - region: Filter by region (e.g., ?region=Africa)
    - currency: Filter by currency code (e.g., ?currency=NGN)
    
    Sorting:
    - sort=gdp_desc: Sort by GDP descending
    - sort=gdp_asc: Sort by GDP ascending
    - sort=name_asc: Sort by name ascending
    - sort=name_desc: Sort by name descending
    
    Examples:
    - GET /countries?region=Africa
    - GET /countries?currency=NGN
    - GET /countries?region=Africa&sort=gdp_desc
    """
    service = CountryService(db)
    countries = service.get_all_countries(region=region, currency=currency, sort=sort)
    return countries

@router.get("/countries/{name}", response_model=CountryResponse)
def get_country(
    name: str,
    db: Session = Depends(get_db)
):
    """
    Get a single country by name (case-insensitive)
    
    Example:
    - GET /countries/Nigeria
    """
    service = CountryService(db)
    country = service.get_country_by_name(name)
    return country

@router.delete("/countries/{name}")
def delete_country(
    name: str,
    db: Session = Depends(get_db)
):
    """
    Delete a country by name
    
    Example:
    - DELETE /countries/Nigeria
    """
    service = CountryService(db)
    service.delete_country(name)
    return {"message": f"Country '{name}' deleted successfully"}