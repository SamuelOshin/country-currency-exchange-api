import httpx
from typing import Dict, List
from app.core.config import settings
from app.utils.exceptions import ExternalAPIException

class ExternalAPIService:
    """Service for fetching data from external APIs"""
    
    @staticmethod
    async def fetch_countries() -> List[Dict]:
        """
        Fetch countries from restcountries.com API
        
        Returns: List of country data dictionaries
        Raises: ExternalAPIException on failure
        """
        try:
            async with httpx.AsyncClient(timeout=settings.API_TIMEOUT) as client:
                response = await client.get(settings.RESTCOUNTRIES_API_URL)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            raise ExternalAPIException(
                "Request timeout while fetching countries",
                api_name="restcountries.com"
            )
        except httpx.HTTPError as e:
            raise ExternalAPIException(
                f"HTTP error while fetching countries: {str(e)}",
                api_name="restcountries.com"
            )
        except Exception as e:
            raise ExternalAPIException(
                f"Unexpected error while fetching countries: {str(e)}",
                api_name="restcountries.com"
            )
    
    @staticmethod
    async def fetch_exchange_rates() -> Dict[str, float]:
        """
        Fetch exchange rates from open.er-api.com
        
        Returns: Dictionary of currency codes to rates
        Raises: ExternalAPIException on failure
        """
        try:
            async with httpx.AsyncClient(timeout=settings.API_TIMEOUT) as client:
                response = await client.get(settings.EXCHANGE_API_URL)
                response.raise_for_status()
                data = response.json()
                
                # Extract rates from response
                if "rates" in data:
                    return data["rates"]
                else:
                    raise ExternalAPIException(
                        "Invalid response format from exchange rate API",
                        api_name="open.er-api.com"
                    )
        except httpx.TimeoutException:
            raise ExternalAPIException(
                "Request timeout while fetching exchange rates",
                api_name="open.er-api.com"
            )
        except httpx.HTTPError as e:
            raise ExternalAPIException(
                f"HTTP error while fetching exchange rates: {str(e)}",
                api_name="open.er-api.com"
            )
        except Exception as e:
            raise ExternalAPIException(
                f"Unexpected error while fetching exchange rates: {str(e)}",
                api_name="open.er-api.com"
            )