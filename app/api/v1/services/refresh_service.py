from decimal import Decimal
from typing import Dict, List
from sqlalchemy.orm import Session
from app.api.v1.services.external_api_service import ExternalAPIService
from app.api.v1.services.image_service import ImageService
from app.api.v1.services.country_service import CountryService
from app.api.v1.repositories.country_repository import CountryRepository
from app.utils.helpers import calculate_gdp
from app.utils.exceptions import ExternalAPIException
import asyncio
import logging

logger = logging.getLogger(__name__)

class RefreshService:
    """Service for orchestrating data refresh from external APIs"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = CountryRepository(db)
        self.country_service = CountryService(db)
        self.external_api = ExternalAPIService()
    
    async def refresh_countries(self) -> dict:
        """
        Main refresh orchestration logic:
        1. Fetch countries from external API
        2. Fetch exchange rates from external API
        3. Process and match data
        4. Upsert to database
        5. Generate summary image
        
        Returns: Summary of refresh operation
        Raises: ExternalAPIException if external APIs fail
        """
        try:
            logger.info("Starting country refresh process")
            
            # Fetch data from external APIs in parallel
            logger.info("Fetching data from external APIs")
            countries_data, exchange_rates = await asyncio.gather(
                self.external_api.fetch_countries(),
                self.external_api.fetch_exchange_rates()
            )
            logger.info(f"Fetched {len(countries_data)} countries and {len(exchange_rates)} exchange rates")
            
            # Process countries
            logger.info("Processing country data")
            processed_countries = self._process_countries(countries_data, exchange_rates)
            
            # Bulk upsert to database
            logger.info(f"Upserting {len(processed_countries)} countries to database")
            count = self.repository.bulk_upsert(processed_countries)
            logger.info(f"Successfully upserted {count} countries")
            
            # Generate summary image (in background)
            logger.info("Generating summary image")
            await self._generate_summary_image()
            
            # Get status
            status = self.country_service.get_status()
            
            logger.info("Refresh completed successfully")
            return {
                "message": "Countries refreshed successfully",
                "countries_processed": count,
                "total_countries": status["total_countries"],
                "last_refreshed_at": status["last_refreshed_at"]
            }
            
        except ExternalAPIException:
            # Re-raise external API exceptions
            logger.error("External API exception during refresh")
            raise
        except Exception as e:
            # Wrap other exceptions
            logger.error(f"Error during refresh: {str(e)}", exc_info=True)
            raise ExternalAPIException(
                f"Error during refresh: {str(e)}",
                api_name="refresh_service"
            )
    
    def _process_countries(
        self,
        countries_data: List[Dict],
        exchange_rates: Dict[str, float]
    ) -> List[dict]:
        """
        Process countries data and match with exchange rates
        
        Currency Handling Rules:
        1. If country has multiple currencies, use only the first
        2. If currencies array is empty:
           - Don't call exchange rate API
           - Set currency_code to None
           - Set exchange_rate to None
           - Set estimated_gdp to 0
        3. If currency_code not in exchange rates:
           - Set exchange_rate to None
           - Set estimated_gdp to None
        """
        processed = []
        
        for country in countries_data:
            country_dict = self._extract_country_data(country, exchange_rates)
            processed.append(country_dict)
        
        return processed
    
    def _extract_country_data(self, country: Dict, exchange_rates: Dict[str, float]) -> dict:
        """Extract and process data for a single country"""
        name = country.get("name", "")
        capital = country.get("capital")
        region = country.get("region")
        population = country.get("population", 0)
        flag_url = country.get("flag")
        currencies = country.get("currencies", [])
        
        # Handle currency
        currency_code = None
        exchange_rate = None
        estimated_gdp = None
        
        if currencies and len(currencies) > 0:
            # Take first currency
            first_currency = currencies[0]
            currency_code = first_currency.get("code")
            
            if currency_code:
                # Try to get exchange rate
                rate = exchange_rates.get(currency_code)
                
                if rate is not None:
                    exchange_rate = Decimal(str(rate))
                    # Calculate GDP with fresh random multiplier
                    estimated_gdp = calculate_gdp(population, exchange_rate)
                else:
                    # Currency not found in exchange rates
                    exchange_rate = None
                    estimated_gdp = None
        else:
            # No currencies - set GDP to 0
            currency_code = None
            exchange_rate = None
            estimated_gdp = Decimal("0")
        
        return {
            "name": name,
            "capital": capital,
            "region": region,
            "population": population,
            "currency_code": currency_code,
            "exchange_rate": exchange_rate,
            "estimated_gdp": estimated_gdp,
            "flag_url": flag_url
        }
    
    async def _generate_summary_image(self):
        """Generate summary image after refresh (runs in thread pool to avoid blocking)"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._generate_image_sync)
    
    def _generate_image_sync(self):
        """Synchronous image generation (called from thread pool)"""
        try:
            status = self.country_service.get_status()
            top_countries = self.country_service.get_top_countries_by_gdp(limit=5)
            
            ImageService.generate_summary_image(
                total_countries=status["total_countries"],
                top_countries=top_countries,
                last_refreshed=status["last_refreshed_at"]
            )
        except Exception as e:
            logger.error(f"Error generating summary image: {e}", exc_info=True)
            # Don't fail the entire refresh if image generation fails