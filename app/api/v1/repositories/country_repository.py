from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from app.api.v1.models.country import Country
from app.api.v1.repositories.base import BaseRepository
from app.utils.helpers import normalize_country_name

class CountryRepository(BaseRepository[Country]):
    """Repository for Country model with specific operations"""
    
    def __init__(self, db: Session):
        super().__init__(Country, db)
    
    def get_by_name(self, name: str) -> Optional[Country]:
        """Get country by name (case-insensitive)"""
        normalized = normalize_country_name(name)
        return self.db.query(Country).filter(
            func.lower(Country.name) == normalized
        ).first()
    
    def get_with_filters(
        self,
        region: Optional[str] = None,
        currency: Optional[str] = None,
        sort_by: Optional[str] = None
    ) -> List[Country]:
        """
        Get countries with optional filters and sorting
        
        Filters:
        - region: Filter by region
        - currency: Filter by currency_code
        
        Sorting:
        - gdp_desc: Sort by estimated_gdp descending
        - gdp_asc: Sort by estimated_gdp ascending
        - name_asc: Sort by name ascending
        - name_desc: Sort by name descending
        """
        query = self.db.query(Country)
        
        # Apply filters
        if region:
            query = query.filter(func.lower(Country.region) == region.lower())
        
        if currency:
            query = query.filter(func.lower(Country.currency_code) == currency.lower())
        
        # Apply sorting
        if sort_by:
            if sort_by == "gdp_desc":
                query = query.order_by(desc(Country.estimated_gdp))
            elif sort_by == "gdp_asc":
                query = query.order_by(asc(Country.estimated_gdp))
            elif sort_by == "name_asc":
                query = query.order_by(asc(Country.name))
            elif sort_by == "name_desc":
                query = query.order_by(desc(Country.name))
        
        return query.all()
    
    def get_top_by_gdp(self, limit: int = 5) -> List[Country]:
        """Get top countries by estimated GDP"""
        return self.db.query(Country).filter(
            Country.estimated_gdp.isnot(None)
        ).order_by(desc(Country.estimated_gdp)).limit(limit).all()
    
    def get_last_refresh_time(self):
        """Get the most recent refresh timestamp"""
        result = self.db.query(func.max(Country.last_refreshed_at)).scalar()
        return result
    
    def upsert_country(self, country_data: dict) -> Country:
        """
        Insert or update country by name
        
        Matches existing countries by name (case-insensitive)
        Updates all fields if exists, inserts if doesn't exist
        """
        existing = self.get_by_name(country_data["name"])
        
        if existing:
            # Update existing country
            for key, value in country_data.items():
                if key != "id":  # Don't update id
                    setattr(existing, key, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new country
            new_country = Country(**country_data)
            return self.create(new_country)
    
    def bulk_upsert(self, countries_data: List[dict]) -> int:
        """
        Bulk upsert countries
        
        Returns: Number of countries processed
        """
        count = 0
        for country_data in countries_data:
            self.upsert_country(country_data)
            count += 1
        return count
    
    def delete_by_name(self, name: str) -> bool:
        """
        Delete country by name (case-insensitive)
        
        Returns: True if deleted, False if not found
        """
        country = self.get_by_name(name)
        if country:
            self.delete(country)
            return True
        return False