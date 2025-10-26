from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, text
from app.api.v1.models.country import Country
from app.api.v1.repositories.base import BaseRepository
from app.utils.helpers import normalize_country_name
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

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
                # Put NULL values last when sorting descending
                query = query.order_by(
                    Country.estimated_gdp.is_(None),
                    desc(Country.estimated_gdp)
                )
            elif sort_by == "gdp_asc":
                # Put NULL values last when sorting ascending
                query = query.order_by(
                    Country.estimated_gdp.is_(None),
                    asc(Country.estimated_gdp)
                )
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
        Bulk upsert countries with optimized batch processing using MySQL's ON DUPLICATE KEY UPDATE
        
        This is the fastest approach for MySQL - uses a single INSERT statement with ON DUPLICATE KEY UPDATE
        which handles both inserts and updates in one query per batch.
        
        Returns: Number of countries processed
        """
        if not countries_data:
            return 0
        
        import time
        start_time = time.time()
        
        # Current timestamp for last_refreshed_at
        now = datetime.utcnow()
        
        logger.info(f"Bulk upserting {len(countries_data)} countries using ON DUPLICATE KEY UPDATE")
        
        # Build values for bulk INSERT ... ON DUPLICATE KEY UPDATE
        values_list = []
        for country_data in countries_data:
            # Escape single quotes
            name = country_data['name'].replace("'", "''")
            capital = country_data.get('capital', '').replace("'", "''") if country_data.get('capital') else ''
            region = country_data.get('region', '').replace("'", "''") if country_data.get('region') else ''
            flag_url = country_data.get('flag_url', '').replace("'", "''") if country_data.get('flag_url') else ''
            currency_code = country_data.get('currency_code', '')
            exchange_rate = country_data.get('exchange_rate')
            estimated_gdp = country_data.get('estimated_gdp')
            population = country_data.get('population', 0)
            
            value = (
                f"('{name}', '{capital}', '{region}', {population}, "
                f"'{currency_code if currency_code else ''}', "
                f"{exchange_rate if exchange_rate is not None else 'NULL'}, "
                f"{estimated_gdp if estimated_gdp is not None else 'NULL'}, "
                f"'{flag_url}', '{now.strftime('%Y-%m-%d %H:%M:%S')}')"
            )
            values_list.append(value)
        
        # Process in batches to avoid hitting MySQL packet size limits
        batch_size = 100
        for i in range(0, len(values_list), batch_size):
            batch = values_list[i:i + batch_size]
            values_str = ", ".join(batch)
            
            # Single INSERT ... ON DUPLICATE KEY UPDATE statement
            upsert_sql = f"""
            INSERT INTO countries (name, capital, region, population, currency_code, exchange_rate, estimated_gdp, flag_url, last_refreshed_at)
            VALUES {values_str}
            ON DUPLICATE KEY UPDATE
                capital = VALUES(capital),
                region = VALUES(region),
                population = VALUES(population),
                currency_code = VALUES(currency_code),
                exchange_rate = VALUES(exchange_rate),
                estimated_gdp = VALUES(estimated_gdp),
                flag_url = VALUES(flag_url),
                last_refreshed_at = VALUES(last_refreshed_at)
            """
            
            self.db.execute(text(upsert_sql))
        
        # Commit everything at once
        logger.info("Committing transaction")
        t5 = time.time()
        self.db.commit()
        logger.info(f"Commit completed in {time.time()-t5:.2f}s")
        
        total_time = time.time() - start_time
        logger.info(f"Total bulk_upsert time: {total_time:.2f}s for {len(countries_data)} countries")
        
        return len(countries_data)
    
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