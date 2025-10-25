import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from decimal import Decimal
from datetime import datetime
from app.api.v1.models.country import Country
from app.utils.exceptions import ExternalAPIException


class TestRefreshEndpoint:
    """Tests for POST /api/v1/countries/refresh endpoint"""

    @pytest.mark.asyncio
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_countries')
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_exchange_rates')
    @patch('app.api.v1.services.image_service.ImageService.generate_summary_image')
    async def test_refresh_countries_success(
        self, 
        mock_image, 
        mock_rates, 
        mock_countries, 
        client, 
        db_session
    ):
        """Test successful refresh with new countries"""
        # Mock external API responses
        mock_countries.return_value = [
            {
                "name": "Nigeria",
                "capital": "Abuja",
                "region": "Africa",
                "population": 206139589,
                "flag": "https://flagcdn.com/ng.svg",
                "currencies": [{"code": "NGN"}]
            },
            {
                "name": "United States",
                "capital": "Washington, D.C.",
                "region": "Americas",
                "population": 331002651,
                "flag": "https://flagcdn.com/us.svg",
                "currencies": [{"code": "USD"}]
            }
        ]
        
        mock_rates.return_value = {
            "NGN": 1600.23,
            "USD": 1.0
        }
        
        mock_image.return_value = None
        
        # Make request
        response = client.post("/api/v1/countries/refresh")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "countries_processed" in data
        assert "total_countries" in data
        assert "last_refreshed_at" in data
        
        assert data["countries_processed"] == 2
        assert data["total_countries"] == 2
        
        # Verify countries were saved to database
        countries = db_session.query(Country).all()
        assert len(countries) == 2

    @pytest.mark.asyncio
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_countries')
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_exchange_rates')
    @patch('app.api.v1.services.image_service.ImageService.generate_summary_image')
    async def test_refresh_updates_existing_countries(
        self, 
        mock_image, 
        mock_rates, 
        mock_countries, 
        client, 
        db_session
    ):
        """Test that refresh updates existing countries"""
        # Create existing country
        existing_country = Country(
            name="Nigeria",
            capital="Abuja",
            region="Africa",
            population=200000000,  # Old population
            currency_code="NGN",
            exchange_rate=Decimal("1500.00"),  # Old rate
            estimated_gdp=Decimal("20000000.00"),
            flag_url="https://flagcdn.com/ng.svg"
        )
        db_session.add(existing_country)
        db_session.commit()
        
        # Mock external API responses with updated data
        mock_countries.return_value = [
            {
                "name": "Nigeria",
                "capital": "Abuja",
                "region": "Africa",
                "population": 206139589,  # Updated population
                "flag": "https://flagcdn.com/ng.svg",
                "currencies": [{"code": "NGN"}]
            }
        ]
        
        mock_rates.return_value = {
            "NGN": 1600.23  # Updated rate
        }
        
        mock_image.return_value = None
        
        # Make request
        response = client.post("/api/v1/countries/refresh")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["total_countries"] == 1
        
        # Verify country was updated
        updated_country = db_session.query(Country).filter_by(name="Nigeria").first()
        assert updated_country.population == 206139589
        assert float(updated_country.exchange_rate) == 1600.23

    @pytest.mark.asyncio
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_countries')
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_exchange_rates')
    @patch('app.api.v1.services.image_service.ImageService.generate_summary_image')
    async def test_refresh_handles_country_without_currency(
        self, 
        mock_image, 
        mock_rates, 
        mock_countries, 
        client, 
        db_session
    ):
        """Test handling countries with no currencies"""
        mock_countries.return_value = [
            {
                "name": "Antarctica",
                "capital": None,
                "region": "Polar",
                "population": 1000,
                "flag": "https://flagcdn.com/aq.svg",
                "currencies": []  # No currency
            }
        ]
        
        mock_rates.return_value = {}
        mock_image.return_value = None
        
        # Make request
        response = client.post("/api/v1/countries/refresh")
        
        # Assertions
        assert response.status_code == 200
        
        # Verify country was saved with null currency
        country = db_session.query(Country).filter_by(name="Antarctica").first()
        assert country is not None
        assert country.currency_code is None
        assert country.exchange_rate is None
        assert country.estimated_gdp == 0

    @pytest.mark.asyncio
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_countries')
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_exchange_rates')
    @patch('app.api.v1.services.image_service.ImageService.generate_summary_image')
    async def test_refresh_handles_currency_not_in_rates(
        self, 
        mock_image, 
        mock_rates, 
        mock_countries, 
        client, 
        db_session
    ):
        """Test handling currencies not found in exchange rates API"""
        mock_countries.return_value = [
            {
                "name": "Wakanda",
                "capital": "Birnin Zana",
                "region": "Africa",
                "population": 6000000,
                "flag": "https://flagcdn.com/wk.svg",
                "currencies": [{"code": "VBR"}]  # Vibranium - not in rates
            }
        ]
        
        mock_rates.return_value = {
            "USD": 1.0,
            "NGN": 1600.23
            # VBR not included
        }
        
        mock_image.return_value = None
        
        # Make request
        response = client.post("/api/v1/countries/refresh")
        
        # Assertions
        assert response.status_code == 200
        
        # Verify country was saved with null exchange_rate and estimated_gdp
        country = db_session.query(Country).filter_by(name="Wakanda").first()
        assert country is not None
        assert country.currency_code == "VBR"
        assert country.exchange_rate is None
        assert country.estimated_gdp is None

    @pytest.mark.asyncio
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_countries')
    async def test_refresh_fails_when_countries_api_unavailable(
        self, 
        mock_countries, 
        client, 
        db_session
    ):
        """Test 503 error when countries API fails"""
        # Mock API failure
        mock_countries.side_effect = ExternalAPIException(
            "Request timeout while fetching countries",
            api_name="restcountries.com"
        )
        
        # Make request
        response = client.post("/api/v1/countries/refresh")
        
        # Assertions
        assert response.status_code == 503
        data = response.json()
        
        assert data["error"] == "External data source unavailable"
        assert "Could not fetch data from restcountries.com" in data["details"]
        
        # Verify no countries were added to database
        countries = db_session.query(Country).all()
        assert len(countries) == 0

    @pytest.mark.asyncio
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_countries')
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_exchange_rates')
    async def test_refresh_fails_when_exchange_api_unavailable(
        self, 
        mock_rates,
        mock_countries, 
        client, 
        db_session
    ):
        """Test 503 error when exchange rates API fails"""
        mock_countries.return_value = [
            {
                "name": "Nigeria",
                "capital": "Abuja",
                "region": "Africa",
                "population": 206139589,
                "flag": "https://flagcdn.com/ng.svg",
                "currencies": [{"code": "NGN"}]
            }
        ]
        
        # Mock exchange API failure
        mock_rates.side_effect = ExternalAPIException(
            "Request timeout while fetching exchange rates",
            api_name="open.er-api.com"
        )
        
        # Make request
        response = client.post("/api/v1/countries/refresh")
        
        # Assertions
        assert response.status_code == 503
        data = response.json()
        
        assert data["error"] == "External data source unavailable"
        assert "Could not fetch data from open.er-api.com" in data["details"]
        
        # Verify no countries were added to database
        countries = db_session.query(Country).all()
        assert len(countries) == 0

    @pytest.mark.asyncio
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_countries')
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_exchange_rates')
    @patch('app.api.v1.services.image_service.ImageService.generate_summary_image')
    async def test_refresh_does_not_modify_db_on_failure(
        self, 
        mock_image,
        mock_rates,
        mock_countries, 
        client, 
        db_session
    ):
        """Test that existing database records are not modified if refresh fails"""
        # Create existing country
        existing_country = Country(
            name="Nigeria",
            capital="Abuja",
            region="Africa",
            population=200000000,
            currency_code="NGN",
            exchange_rate=Decimal("1500.00"),
            estimated_gdp=Decimal("20000000.00"),
            flag_url="https://flagcdn.com/ng.svg"
        )
        db_session.add(existing_country)
        db_session.commit()
        original_population = existing_country.population
        
        # Mock API failure
        mock_countries.side_effect = ExternalAPIException(
            "API unavailable",
            api_name="restcountries.com"
        )
        
        # Make request
        response = client.post("/api/v1/countries/refresh")
        
        # Assertions
        assert response.status_code == 503
        
        # Verify existing country was NOT modified
        db_session.refresh(existing_country)
        assert existing_country.population == original_population

    @pytest.mark.asyncio
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_countries')
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_exchange_rates')
    @patch('app.api.v1.services.image_service.ImageService.generate_summary_image')
    async def test_refresh_handles_multiple_currencies(
        self, 
        mock_image, 
        mock_rates, 
        mock_countries, 
        client, 
        db_session
    ):
        """Test that only first currency is stored for countries with multiple currencies"""
        mock_countries.return_value = [
            {
                "name": "Switzerland",
                "capital": "Bern",
                "region": "Europe",
                "population": 8654622,
                "flag": "https://flagcdn.com/ch.svg",
                "currencies": [
                    {"code": "CHF"},
                    {"code": "EUR"}  # Multiple currencies
                ]
            }
        ]
        
        mock_rates.return_value = {
            "CHF": 0.92,
            "EUR": 0.85
        }
        
        mock_image.return_value = None
        
        # Make request
        response = client.post("/api/v1/countries/refresh")
        
        # Assertions
        assert response.status_code == 200
        
        # Verify only first currency was stored
        country = db_session.query(Country).filter_by(name="Switzerland").first()
        assert country is not None
        assert country.currency_code == "CHF"

    @pytest.mark.asyncio
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_countries')
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_exchange_rates')
    @patch('app.api.v1.services.image_service.ImageService.generate_summary_image')
    async def test_refresh_updates_last_refreshed_timestamp(
        self, 
        mock_image, 
        mock_rates, 
        mock_countries, 
        client, 
        db_session
    ):
        """Test that last_refreshed_at timestamp is updated"""
        mock_countries.return_value = [
            {
                "name": "Nigeria",
                "capital": "Abuja",
                "region": "Africa",
                "population": 206139589,
                "flag": "https://flagcdn.com/ng.svg",
                "currencies": [{"code": "NGN"}]
            }
        ]
        
        mock_rates.return_value = {"NGN": 1600.23}
        mock_image.return_value = None
        
        # Make request
        response = client.post("/api/v1/countries/refresh")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        assert "last_refreshed_at" in data
        assert data["last_refreshed_at"] is not None
        
        # Verify country has timestamp
        country = db_session.query(Country).filter_by(name="Nigeria").first()
        assert country.last_refreshed_at is not None

    @pytest.mark.asyncio
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_countries')
    @patch('app.api.v1.services.external_api_service.ExternalAPIService.fetch_exchange_rates')
    @patch('app.api.v1.services.image_service.ImageService.generate_summary_image')
    async def test_refresh_generates_new_gdp_on_update(
        self, 
        mock_image, 
        mock_rates, 
        mock_countries, 
        client, 
        db_session
    ):
        """Test that estimated_gdp is recalculated with new random multiplier on refresh"""
        # Create existing country
        existing_country = Country(
            name="Nigeria",
            capital="Abuja",
            region="Africa",
            population=206139589,
            currency_code="NGN",
            exchange_rate=Decimal("1600.23"),
            estimated_gdp=Decimal("257674481.25"),
            flag_url="https://flagcdn.com/ng.svg"
        )
        db_session.add(existing_country)
        db_session.commit()
        old_gdp = existing_country.estimated_gdp
        
        # Mock refresh with same data
        mock_countries.return_value = [
            {
                "name": "Nigeria",
                "capital": "Abuja",
                "region": "Africa",
                "population": 206139589,
                "flag": "https://flagcdn.com/ng.svg",
                "currencies": [{"code": "NGN"}]
            }
        ]
        
        mock_rates.return_value = {"NGN": 1600.23}
        mock_image.return_value = None
        
        # Make request
        response = client.post("/api/v1/countries/refresh")
        
        # Assertions
        assert response.status_code == 200
        
        # Verify GDP was recalculated (should be different due to new random multiplier)
        db_session.refresh(existing_country)
        # GDP should be in valid range: population * (1000-2000) / exchange_rate
        assert existing_country.estimated_gdp is not None
        min_gdp = Decimal(206139589) * Decimal(1000) / Decimal("1600.23")
        max_gdp = Decimal(206139589) * Decimal(2000) / Decimal("1600.23")
        assert min_gdp <= existing_country.estimated_gdp <= max_gdp
