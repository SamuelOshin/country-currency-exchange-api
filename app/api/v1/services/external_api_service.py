import httpx
from typing import Dict, List
from app.core.config import settings
from app.utils.exceptions import ExternalAPIException
import logging

logger = logging.getLogger(__name__)

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
            # Configure client with proper SSL and timeout handling
            async with httpx.AsyncClient(
                timeout=settings.API_TIMEOUT,
                verify=True,  # Enable SSL verification
                follow_redirects=True
            ) as client:
                logger.info(f"Fetching countries from {settings.RESTCOUNTRIES_API_URL}")
                response = await client.get(settings.RESTCOUNTRIES_API_URL)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as e:
            logger.error(f"Timeout fetching countries: {str(e)}")
            raise ExternalAPIException(
                "Request timeout while fetching countries",
                api_name="restcountries.com"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP status error fetching countries: {e.response.status_code} - {str(e)}")
            raise ExternalAPIException(
                f"HTTP error while fetching countries: {e.response.status_code}",
                api_name="restcountries.com"
            )
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching countries: {str(e)}")
            raise ExternalAPIException(
                f"HTTP error while fetching countries: {str(e)}",
                api_name="restcountries.com"
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching countries: {str(e)}", exc_info=True)
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
            # Configure client with proper SSL and timeout handling
            async with httpx.AsyncClient(
                timeout=settings.API_TIMEOUT,
                verify=True,  # Enable SSL verification
                follow_redirects=True
            ) as client:
                logger.info(f"Fetching exchange rates from {settings.EXCHANGE_API_URL}")
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
        except httpx.TimeoutException as e:
            logger.error(f"Timeout fetching exchange rates: {str(e)}")
            raise ExternalAPIException(
                "Request timeout while fetching exchange rates",
                api_name="open.er-api.com"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP status error fetching exchange rates: {e.response.status_code} - {str(e)}")
            raise ExternalAPIException(
                f"HTTP error while fetching exchange rates: {e.response.status_code}",
                api_name="open.er-api.com"
            )
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching exchange rates: {str(e)}")
            raise ExternalAPIException(
                f"HTTP error while fetching exchange rates: {str(e)}",
                api_name="open.er-api.com"
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching exchange rates: {str(e)}", exc_info=True)
            raise ExternalAPIException(
                f"Unexpected error while fetching exchange rates: {str(e)}",
                api_name="open.er-api.com"
            )