"""
Comprehensive validation test script for HNGi13 Country Currency Exchange API
Tests all 7 requirement categories with scoring
"""
import pytest
from datetime import datetime
from decimal import Decimal


class TestResults:
    """Track test results and scoring"""
    def __init__(self):
        self.results = {}
        self.total_score = 0
        self.max_score = 100
        
    def add_result(self, test_name, points, max_points, passed):
        self.results[test_name] = {
            'points': points if passed else 0,
            'max_points': max_points,
            'passed': passed
        }
        self.total_score += points if passed else 0
        
    def print_summary(self):
        print("\n" + "="*60)
        print("VALIDATION TEST RESULTS SUMMARY")
        print("="*60)
        for test, result in self.results.items():
            status = "✓" if result['passed'] else "✗"
            print(f"{status} {test}: {result['points']}/{result['max_points']} pts")
        print("="*60)
        print(f"TOTAL SCORE: {self.total_score}/{self.max_score}")
        print("="*60)


@pytest.fixture(scope="module")
def test_results():
    """Fixture to track test results across all tests"""
    return TestResults()


# ============================================================
# TEST 1: POST /countries/refresh (25 points)
# ============================================================

def test_1_refresh_endpoint_accessible(client, test_results):
    """Refresh endpoint accessible (3 pts)"""
    response = client.post("/api/v1/countries/refresh")
    passed = response.status_code in [200, 201]
    test_results.add_result("1.1 Refresh endpoint accessible", 3, 3, passed)
    assert passed, f"Expected status 200/201, got {response.status_code}"


def test_1_refresh_returns_correct_status(client, test_results):
    """Returns correct status code (2 pts)"""
    response = client.post("/api/v1/countries/refresh")
    passed = response.status_code == 200
    test_results.add_result("1.2 Returns correct status code", 2, 2, passed)
    assert passed, f"Expected status 200, got {response.status_code}"


def test_1_countries_fetched_and_stored(client, db_session, test_results):
    """Countries fetched and stored (100 countries) (5 pts)"""
    # Refresh data
    response = client.post("/api/v1/countries/refresh")
    assert response.status_code == 200
    
    # Check database
    from app.api.v1.models.country import Country
    count = db_session.query(Country).count()
    
    # Pass if we have at least 100 countries
    passed = count >= 100
    test_results.add_result("1.3 Countries fetched and stored (100+ countries)", 5, 5, passed)
    assert passed, f"Expected at least 100 countries, got {count}"


def test_1_currency_codes_properly_stored(client, db_session, test_results):
    """Currency codes properly stored (5 pts)"""
    # Refresh data
    client.post("/api/v1/countries/refresh")
    
    from app.api.v1.models.country import Country
    countries_with_currency = db_session.query(Country).filter(
        Country.currency_code.isnot(None),
        Country.currency_code != ""
    ).count()
    
    # At least 90% of countries should have currency codes
    total_countries = db_session.query(Country).count()
    passed = countries_with_currency >= (total_countries * 0.9)
    test_results.add_result("1.4 Currency codes properly stored", 5, 5, passed)
    assert passed, f"Expected 90%+ countries with currency codes, got {countries_with_currency}/{total_countries}"


def test_1_exchange_rates_calculated(client, db_session, test_results):
    """Exchange rates calculated (5 pts)"""
    # Refresh data
    client.post("/api/v1/countries/refresh")
    
    from app.api.v1.models.country import Country
    countries_with_rates = db_session.query(Country).filter(
        Country.exchange_rate.isnot(None),
        Country.exchange_rate > 0
    ).count()
    
    # At least 80% of countries should have exchange rates
    total_countries = db_session.query(Country).count()
    passed = countries_with_rates >= (total_countries * 0.8)
    test_results.add_result("1.5 Exchange rates calculated", 5, 5, passed)
    assert passed, f"Expected 80%+ countries with exchange rates, got {countries_with_rates}/{total_countries}"


def test_1_estimated_gdp_calculated(client, db_session, test_results):
    """Estimated GDP calculated correctly (5 pts)"""
    # Refresh data
    client.post("/api/v1/countries/refresh")
    
    from app.api.v1.models.country import Country
    countries_with_gdp = db_session.query(Country).filter(
        Country.estimated_gdp.isnot(None),
        Country.estimated_gdp > 0
    ).count()
    
    # At least 80% of countries should have GDP estimates
    total_countries = db_session.query(Country).count()
    passed = countries_with_gdp >= (total_countries * 0.8)
    test_results.add_result("1.6 Estimated GDP calculated correctly", 5, 5, passed)
    assert passed, f"Expected 80%+ countries with GDP estimates, got {countries_with_gdp}/{total_countries}"


# ============================================================
# TEST 2: GET /countries (filters & sorting) (25 points)
# ============================================================

def test_2_basic_get_countries_works(client, db_session, test_results):
    """Basic GET /countries works (5 pts)"""
    # Add test data
    from app.api.v1.models.country import Country
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
    passed = response.status_code == 200 and len(response.json()) > 0
    test_results.add_result("2.1 Basic GET /countries works", 5, 5, passed)
    assert passed, f"Expected status 200 with data, got {response.status_code}"


def test_2_returns_correct_structure(client, db_session, test_results):
    """Returns correct structure (5 pts)"""
    from app.api.v1.models.country import Country
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
    data = response.json()
    
    required_fields = ['name', 'capital', 'region', 'population', 'currency_code', 
                      'exchange_rate', 'estimated_gdp', 'flag_url']
    passed = all(field in data[0] for field in required_fields)
    test_results.add_result("2.2 Returns correct structure", 5, 5, passed)
    assert passed, f"Missing required fields in response"


def test_2_region_filter_works(client, db_session, test_results):
    """Region filter works (5 pts)"""
    from app.api.v1.models.country import Country
    
    # Add test countries
    nigeria = Country(
        name="Nigeria", region="Africa", population=206139589, 
        currency_code="NGN", exchange_rate=Decimal("1600.23"),
        estimated_gdp=Decimal("25767448125.2")
    )
    usa = Country(
        name="United States", region="Americas", population=331002651, 
        currency_code="USD", exchange_rate=Decimal("1.0"),
        estimated_gdp=Decimal("23315080560651.0")
    )
    
    db_session.add_all([nigeria, usa])
    db_session.commit()
    
    response = client.get("/api/v1/countries?region=Africa")
    passed = response.status_code == 200
    
    if passed:
        data = response.json()
        passed = len(data) == 1 and data[0]["name"] == "Nigeria"
    
    test_results.add_result("2.3 Region filter works", 5, 5, passed)
    assert passed, f"Region filter failed with status {response.status_code}"


def test_2_currency_filter_works(client, db_session, test_results):
    """Currency filter works (5 pts)"""
    from app.api.v1.models.country import Country
    
    # Add test countries
    nigeria = Country(
        name="Nigeria", region="Africa", population=206139589, 
        currency_code="NGN", exchange_rate=Decimal("1600.23"),
        estimated_gdp=Decimal("25767448125.2")
    )
    usa = Country(
        name="United States", region="Americas", population=331002651, 
        currency_code="USD", exchange_rate=Decimal("1.0"),
        estimated_gdp=Decimal("23315080560651.0")
    )
    
    db_session.add_all([nigeria, usa])
    db_session.commit()
    
    response = client.get("/api/v1/countries?currency=NGN")
    passed = response.status_code == 200
    
    if passed:
        data = response.json()
        passed = len(data) == 1 and data[0]["currency_code"] == "NGN"
    
    test_results.add_result("2.4 Currency filter works", 5, 5, passed)
    assert passed, f"Currency filter failed"


def test_2_sorting_by_gdp_works(client, db_session, test_results):
    """Sorting by GDP works (5 pts)"""
    from app.api.v1.models.country import Country
    
    # Add test countries with different GDPs
    countries = [
        Country(name="Country A", region="Africa", population=1000000, 
                currency_code="AAA", exchange_rate=Decimal("1.0"),
                estimated_gdp=Decimal("1000000.0")),
        Country(name="Country B", region="Africa", population=2000000, 
                currency_code="BBB", exchange_rate=Decimal("1.0"),
                estimated_gdp=Decimal("5000000.0")),
        Country(name="Country C", region="Africa", population=3000000, 
                currency_code="CCC", exchange_rate=Decimal("1.0"),
                estimated_gdp=Decimal("3000000.0")),
    ]
    
    db_session.add_all(countries)
    db_session.commit()
    
    response = client.get("/api/v1/countries?sort=gdp_desc")
    passed = response.status_code == 200
    
    if passed:
        data = response.json()
        # Check if sorted in descending order
        gdps = [float(c['estimated_gdp']) for c in data]
        passed = gdps == sorted(gdps, reverse=True)
    
    test_results.add_result("2.5 Sorting by GDP works", 5, 5, passed)
    assert passed, f"GDP sorting failed"


# ============================================================
# TEST 3: GET /countries/:name (10 points)
# ============================================================

def test_3_get_specific_country_works(client, db_session, test_results):
    """Get specific country works (5 pts)"""
    from app.api.v1.models.country import Country
    
    country = Country(
        name="Nigeria",
        capital="Abuja",
        region="Africa",
        population=206139589,
        currency_code="NGN",
        exchange_rate=Decimal("1600.23"),
        estimated_gdp=Decimal("25767448125.2")
    )
    db_session.add(country)
    db_session.commit()
    
    response = client.get("/api/v1/countries/Nigeria")
    passed = response.status_code == 200
    test_results.add_result("3.1 Get specific country works", 5, 5, passed)
    assert passed, f"Expected status 200, got {response.status_code}"


def test_3_returns_correct_country_data(client, db_session, test_results):
    """Returns correct country data (3 pts)"""
    from app.api.v1.models.country import Country
    
    country = Country(
        name="Nigeria",
        capital="Abuja",
        region="Africa",
        population=206139589,
        currency_code="NGN",
        exchange_rate=Decimal("1600.23"),
        estimated_gdp=Decimal("25767448125.2")
    )
    db_session.add(country)
    db_session.commit()
    
    response = client.get("/api/v1/countries/Nigeria")
    data = response.json()
    
    passed = (
        response.status_code == 200 and
        data["name"] == "Nigeria" and
        data["capital"] == "Abuja" and
        data["currency_code"] == "NGN"
    )
    test_results.add_result("3.2 Returns correct country data", 3, 3, passed)
    assert passed, f"Country data mismatch"


def test_3_returns_404_for_nonexistent_country(client, test_results):
    """Returns 404 for non-existent country (2 pts)"""
    response = client.get("/api/v1/countries/NonExistentCountry")
    passed = response.status_code == 404
    test_results.add_result("3.3 Returns 404 for non-existent country", 2, 2, passed)
    assert passed, f"Expected status 404, got {response.status_code}"


# ============================================================
# TEST 4: DELETE /countries/:name (10 points)
# ============================================================

def test_4_delete_endpoint_works(client, db_session, test_results):
    """Delete endpoint works (5 pts)"""
    from app.api.v1.models.country import Country
    
    country = Country(
        name="Nigeria",
        region="Africa",
        population=206139589,
        currency_code="NGN"
    )
    db_session.add(country)
    db_session.commit()
    
    response = client.delete("/api/v1/countries/Nigeria")
    passed = response.status_code == 200
    test_results.add_result("4.1 Delete endpoint works", 5, 5, passed)
    assert passed, f"Expected status 200, got {response.status_code}"


def test_4_country_actually_removed(client, db_session, test_results):
    """Country actually removed from database (3 pts)"""
    from app.api.v1.models.country import Country
    
    country = Country(
        name="Nigeria",
        region="Africa",
        population=206139589,
        currency_code="NGN"
    )
    db_session.add(country)
    db_session.commit()
    
    client.delete("/api/v1/countries/Nigeria")
    
    # Verify deletion
    deleted_country = db_session.query(Country).filter(
        Country.name == "Nigeria"
    ).first()
    
    passed = deleted_country is None
    test_results.add_result("4.2 Country actually removed from database", 3, 3, passed)
    assert passed, "Country was not removed from database"


def test_4_returns_404_for_deleting_nonexistent(client, test_results):
    """Returns 404 for deleting non-existent country (2 pts)"""
    response = client.delete("/api/v1/countries/NonExistentCountry")
    passed = response.status_code == 404
    test_results.add_result("4.3 Returns 404 for deleting non-existent country", 2, 2, passed)
    assert passed, f"Expected status 404, got {response.status_code}"


# ============================================================
# TEST 5: GET /status (10 points)
# ============================================================

def test_5_status_endpoint_accessible(client, test_results):
    """Status endpoint accessible (3 pts)"""
    response = client.get("/api/v1/status")
    passed = response.status_code == 200
    test_results.add_result("5.1 Status endpoint accessible", 3, 3, passed)
    assert passed, f"Expected status 200, got {response.status_code}"


def test_5_returns_total_countries_field(client, db_session, test_results):
    """Returns total_countries field (3 pts)"""
    from app.api.v1.models.country import Country
    
    # Add a country
    country = Country(
        name="Nigeria",
        region="Africa",
        population=206139589,
        currency_code="NGN"
    )
    db_session.add(country)
    db_session.commit()
    
    response = client.get("/api/v1/status")
    data = response.json()
    
    passed = "total_countries" in data and data["total_countries"] >= 0
    test_results.add_result("5.2 Returns total_countries field", 3, 3, passed)
    assert passed, "total_countries field missing or invalid"


def test_5_returns_last_refreshed_at_field(client, test_results):
    """Returns last_refreshed_at field (2 pts)"""
    response = client.get("/api/v1/status")
    data = response.json()
    
    passed = "last_refreshed_at" in data
    test_results.add_result("5.3 Returns last_refreshed_at field", 2, 2, passed)
    assert passed, "last_refreshed_at field missing"


def test_5_valid_timestamp_format(client, test_results):
    """Valid timestamp format (2 pts)"""
    response = client.get("/api/v1/status")
    data = response.json()
    
    passed = False
    if "last_refreshed_at" in data:
        timestamp = data["last_refreshed_at"]
        if timestamp is None:
            passed = True  # Null is acceptable if never refreshed
        else:
            try:
                # Try parsing ISO format
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                passed = True
            except:
                passed = False
    
    test_results.add_result("5.4 Valid timestamp format", 2, 2, passed)
    assert passed, "Invalid timestamp format"


# ============================================================
# TEST 6: GET /countries/image (10 points)
# ============================================================

def test_6_image_endpoint_accessible(client, test_results):
    """Image endpoint accessible (3 pts)"""
    response = client.get("/api/v1/countries/image")
    passed = response.status_code == 200
    test_results.add_result("6.1 Image endpoint accessible", 3, 3, passed)
    assert passed, f"Expected status 200, got {response.status_code}"


def test_6_correct_content_type(client, test_results):
    """Correct Content-Type: image/png (3 pts)"""
    response = client.get("/api/v1/countries/image")
    passed = response.headers.get("content-type") == "image/png"
    test_results.add_result("6.2 Correct Content-Type: image/png", 3, 3, passed)
    assert passed, f"Expected image/png, got {response.headers.get('content-type')}"


def test_6_returns_image_content(client, test_results):
    """Returns image content (4 pts)"""
    response = client.get("/api/v1/countries/image")
    
    # Check if response has content and it's binary
    passed = (
        response.status_code == 200 and
        len(response.content) > 1000 and  # At least 1KB
        response.content[:4] == b'\x89PNG'  # PNG magic number
    )
    test_results.add_result("6.3 Returns image content", 4, 4, passed)
    assert passed, f"Invalid image content (size: {len(response.content)} bytes)"


# ============================================================
# TEST 7: Error Handling & Validation (10 points)
# ============================================================

def test_7_404_errors_return_proper_json(client, test_results):
    """404 errors return proper JSON format (3 pts)"""
    response = client.get("/api/v1/countries/NonExistentCountry")
    
    passed = False
    if response.status_code == 404:
        try:
            data = response.json()
            # Check for either 'detail' or 'error' field (both are valid JSON error formats)
            passed = isinstance(data, dict) and ('detail' in data or 'error' in data)
        except:
            passed = False
    
    test_results.add_result("7.1 404 errors return proper JSON format", 3, 3, passed)
    assert passed, "404 errors not returning proper JSON"


def test_7_consistent_error_response_structure(client, test_results):
    """Consistent error response structure (JSON) (4 pts)"""
    # Test multiple error endpoints
    responses = [
        client.get("/api/v1/countries/NonExistent1"),
        client.delete("/api/v1/countries/NonExistent2"),
    ]
    
    passed = True
    for response in responses:
        if response.status_code >= 400:
            try:
                data = response.json()
                # Check for either 'detail' or 'error' field (both are valid)
                if not isinstance(data, dict) or not ('detail' in data or 'error' in data):
                    passed = False
                    break
            except:
                passed = False
                break
    
    test_results.add_result("7.2 Consistent error response structure", 4, 4, passed)
    assert passed, "Inconsistent error response structure"


def test_7_error_handling_implemented(client, db_session, test_results):
    """Error handling implemented (3 pts)"""
    from app.api.v1.models.country import Country
    
    # Add a country
    country = Country(
        name="Nigeria",
        region="Africa",
        population=206139589,
        currency_code="NGN"
    )
    db_session.add(country)
    db_session.commit()
    
    # Test various error scenarios
    error_tests = [
        client.get("/api/v1/countries/NonExistent"),  # 404
        client.delete("/api/v1/countries/NonExistent"),  # 404
    ]
    
    passed = all(r.status_code in [404, 422] for r in error_tests)
    test_results.add_result("7.3 Error handling implemented", 3, 3, passed)
    assert passed, "Error handling not properly implemented"


# ============================================================
# Final Summary
# ============================================================

def test_zzz_print_final_results(test_results):
    """Print final test results summary"""
    test_results.print_summary()
    
    # Assert overall passing grade (70%)
    passing_score = test_results.max_score * 0.7
    assert test_results.total_score >= passing_score, \
        f"Overall score {test_results.total_score}/{test_results.max_score} below passing threshold ({passing_score})"
