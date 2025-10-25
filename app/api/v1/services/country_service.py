from typing import List, Optional
from sqlalchemy.orm import Session
from app.api.v1.models.country import Country
from app.api.v1.repositories.country_repository import CountryRepository
from app.utils.exceptions import CountryNotFoundException

class CountryService:
    """Service for country business logic"""
    
    def __init__(self, db: Session):
        self.repository = CountryRepository(db)
    
    def get_all_countries(
        self,
        region: Optional[str] = None,
        currency: Optional[str] = None,
        sort: Optional[str] = None
    ) -> List[Country]:
        """
        Get all countries with optional filters and sorting
        
        Args:
            region: Filter by region (e.g., "Africa")
            currency: Filter by currency code (e.g., "NGN")
            sort: Sort order (e.g., "gdp_desc", "gdp_asc", "name_asc", "name_desc")
        """
        return self.repository.get_with_filters(
            region=region,
            currency=currency,
            sort_by=sort
        )
    
    def get_country_by_name(self, name: str) -> Country:
        """
        Get a single country by name (case-insensitive)
        
        Raises: CountryNotFoundException if not found
        """
        country = self.repository.get_by_name(name)
        if not country:
            raise CountryNotFoundException(f"Country '{name}' not found")
        return country
    
    def delete_country(self, name: str) -> None:
        """
        Delete a country by name
        
        Raises: CountryNotFoundException if not found
        """
        deleted = self.repository.delete_by_name(name)
        if not deleted:
            raise CountryNotFoundException(f"Country '{name}' not found")
    
    def get_status(self) -> dict:
        """Get database status (total countries and last refresh time)"""
        total = self.repository.count()
        last_refresh = self.repository.get_last_refresh_time()
        
        return {
            "total_countries": total,
            "last_refreshed_at": last_refresh
        }
    
    def get_top_countries_by_gdp(self, limit: int = 5) -> List[Country]:
        """Get top countries by estimated GDP"""
        return self.repository.get_top_by_gdp(limit=limit)