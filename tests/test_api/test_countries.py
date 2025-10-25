import pytest
from decimal import Decimal
from app.api.v1.models.country import Country

def test_get_countries_empty(client):
    """Test getting countries when database is empty"""
    response = client.get("/api/v1/countries")
    assert response.status_code == 200
    assert response.json() == []

def test_get_countries_with_data(client, db_session):
    """Test getting countries with data"""
    # Create test country
    country = Country(
        name="Nigeria",
        capital="Abuja",
        region="Africa",
        population=206139589,
        currency_code="NGN",
        exchange_rate=Decimal("1600.23"),
        estimated_gdp=Decimal("25767448125.2"),
        flag_url="https://flagcdn.com/ng.svg"
    )
    db_session.add(country)
    db_session.commit()
    
    response = client.get("/api/v1/countries")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Nigeria"

def test_get_countries_filter_by_region(client, db_session):
    """Test filtering countries by region"""
    # Create test countries
    nigeria = Country(name="Nigeria", region="Africa", population=206139589, currency_code="NGN")
    usa = Country(name="United States", region="Americas", population=331002651, currency_code="USD")
    
    db_session.add_all([nigeria, usa])
    db_session.commit()
    
    response = client.get("/api/v1/countries?region=Africa")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Nigeria"

def test_get_country_by_name(client, db_session):
    """Test getting a single country by name"""
    country = Country(name="Nigeria", region="Africa", population=206139589, currency_code="NGN")
    db_session.add(country)
    db_session.commit()
    
    response = client.get("/api/v1/countries/Nigeria")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Nigeria"

def test_get_country_not_found(client):
    """Test getting a non-existent country"""
    response = client.get("/api/v1/countries/Wakanda")
    assert response.status_code == 404
    assert "error" in response.json()

def test_delete_country(client, db_session):
    """Test deleting a country"""
    country = Country(name="Nigeria", region="Africa", population=206139589, currency_code="NGN")
    db_session.add(country)
    db_session.commit()
    
    response = client.delete("/api/v1/countries/Nigeria")
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get("/api/v1/countries/Nigeria")
    assert response.status_code == 404

def test_delete_country_not_found(client):
    """Test deleting a non-existent country"""
    response = client.delete("/api/v1/countries/Wakanda")
    assert response.status_code == 404