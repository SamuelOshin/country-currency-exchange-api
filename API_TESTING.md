# API Testing Guide

Complete guide for testing all API endpoints.

## Base URL

**Local**: `http://localhost:8000`  
**Production**: `https://your-domain.com`

---

## 1. Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy"
}
```

---

## 2. Root Endpoint

```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
  "message": "Country Currency & Exchange API",
  "version": "1.0.0",
  "docs": "/docs",
  "endpoints": {
    "refresh": "POST /api/v1/countries/refresh",
    "countries": "GET /api/v1/countries",
    "country": "GET /api/v1/countries/{name}",
    "delete": "DELETE /api/v1/countries/{name}",
    "status": "GET /api/v1/status",
    "image": "GET /api/v1/countries/image"
  }
}
```

---

## 3. Refresh Countries (Initial Data Load)

```bash
curl -X POST http://localhost:8000/api/v1/countries/refresh
```

**Expected Response:**
```json
{
  "message": "Countries refreshed successfully",
  "countries_processed": 250,
  "total_countries": 250,
  "last_refreshed_at": "2025-10-25T18:30:45.123456"
}
```

**Error Responses:**

503 - External API unavailable:
```json
{
  "error": "External data source unavailable",
  "details": "Could not fetch data from restcountries.com"
}
```

---

## 4. Get All Countries

```bash
curl http://localhost:8000/api/v1/countries
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "name": "Nigeria",
    "capital": "Abuja",
    "region": "Africa",
    "population": 206139589,
    "currency_code": "NGN",
    "exchange_rate": 1600.23,
    "estimated_gdp": 25767448125.2,
    "flag_url": "https://flagcdn.com/ng.svg",
    "last_refreshed_at": "2025-10-25T18:30:45.123456"
  },
  ...
]
```

---

## 5. Filter by Region

```bash
curl "http://localhost:8000/api/v1/countries?region=Africa"
```

**Test Cases:**
```bash
# Africa
curl "http://localhost:8000/api/v1/countries?region=Africa"

# Europe
curl "http://localhost:8000/api/v1/countries?region=Europe"

# Asia
curl "http://localhost:8000/api/v1/countries?region=Asia"

# Americas
curl "http://localhost:8000/api/v1/countries?region=Americas"

# Oceania
curl "http://localhost:8000/api/v1/countries?region=Oceania"
```

---

## 6. Filter by Currency

```bash
curl "http://localhost:8000/api/v1/countries?currency=NGN"
```

**Test Cases:**
```bash
# Nigerian Naira
curl "http://localhost:8000/api/v1/countries?currency=NGN"

# US Dollar
curl "http://localhost:8000/api/v1/countries?currency=USD"

# Euro
curl "http://localhost:8000/api/v1/countries?currency=EUR"

# British Pound
curl "http://localhost:8000/api/v1/countries?currency=GBP"
```

---

## 7. Sort Countries

```bash
# Sort by GDP descending
curl "http://localhost:8000/api/v1/countries?sort=gdp_desc"

# Sort by GDP ascending
curl "http://localhost:8000/api/v1/countries?sort=gdp_asc"

# Sort by name ascending
curl "http://localhost:8000/api/v1/countries?sort=name_asc"

# Sort by name descending
curl "http://localhost:8000/api/v1/countries?sort=name_desc"
```

---

## 8. Combined Filters

```bash
# Africa countries sorted by GDP
curl "http://localhost:8000/api/v1/countries?region=Africa&sort=gdp_desc"

# USD countries in Americas
curl "http://localhost:8000/api/v1/countries?region=Americas&currency=USD"

# All filters combined
curl "http://localhost:8000/api/v1/countries?region=Africa&currency=NGN&sort=gdp_desc"
```

---

## 9. Get Single Country

```bash
curl http://localhost:8000/api/v1/countries/Nigeria
```

**Expected Response:**
```json
{
  "id": 1,
  "name": "Nigeria",
  "capital": "Abuja",
  "region": "Africa",
  "population": 206139589,
  "currency_code": "NGN",
  "exchange_rate": 1600.23,
  "estimated_gdp": 25767448125.2,
  "flag_url": "https://flagcdn.com/ng.svg",
  "last_refreshed_at": "2025-10-25T18:30:45.123456"
}
```

**Test Cases:**
```bash
# Case insensitive
curl http://localhost:8000/api/v1/countries/nigeria
curl http://localhost:8000/api/v1/countries/NIGERIA
curl http://localhost:8000/api/v1/countries/Nigeria

# Other countries
curl http://localhost:8000/api/v1/countries/Ghana
curl http://localhost:8000/api/v1/countries/Kenya
curl http://localhost:8000/api/v1/countries/USA
```

**Error Response (404):**
```bash
curl http://localhost:8000/api/v1/countries/Wakanda
```
```json
{
  "error": "Country not found"
}
```

---

## 10. Delete Country

```bash
curl -X DELETE http://localhost:8000/api/v1/countries/Nigeria
```

**Expected Response:**
```json
{
  "message": "Country 'Nigeria' deleted successfully"
}
```

**Error Response (404):**
```bash
curl -X DELETE http://localhost:8000/api/v1/countries/Wakanda
```
```json
{
  "error": "Country not found"
}
```

---

## 11. Get Status

```bash
curl http://localhost:8000/api/v1/status
```

**Expected Response:**
```json
{
  "total_countries": 250,
  "last_refreshed_at": "2025-10-25T18:30:45.123456"
}
```

---

## 12. Get Summary Image

```bash
curl http://localhost:8000/api/v1/countries/image --output summary.png
```

**View image:**
```bash
open summary.png  # macOS
xdg-open summary.png  # Linux
start summary.png  # Windows
```

**Error Response (404) - Before refresh:**
```bash
curl http://localhost:8000/api/v1/countries/image
```
```json
{
  "error": "Summary image not found"
}
```

---

## Python Testing Script

Save as `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, expected_status, description):
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Method: {method} {endpoint}")
    
    if method == "GET":
        response = requests.get(url)
    elif method == "POST":
        response = requests.post(url)
    elif method == "DELETE":
        response = requests.delete(url)
    
    print(f"Status: {response.status_code} (Expected: {expected_status})")
    
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text}")
    
    success = response.status_code == expected_status
    print(f"Result: {'✅ PASS' if success else '❌ FAIL'}")
    return success

# Run tests
print("🚀 Starting API Tests")

tests = [
    ("GET", "/health", 200, "Health Check"),
    ("GET", "/", 200, "Root Endpoint"),
    ("POST", "/api/v1/countries/refresh", 200, "Refresh Countries"),
    ("GET", "/api/v1/countries", 200, "Get All Countries"),
    ("GET", "/api/v1/countries?region=Africa", 200, "Filter by Region"),
    ("GET", "/api/v1/countries?currency=NGN", 200, "Filter by Currency"),
    ("GET", "/api/v1/countries?sort=gdp_desc", 200, "Sort by GDP"),
    ("GET", "/api/v1/countries/Nigeria", 200, "Get Single Country"),
    ("GET", "/api/v1/status", 200, "Get Status"),
    ("GET", "/api/v1/countries/image", 200, "Get Summary Image"),
    ("GET", "/api/v1/countries/Wakanda", 404, "Country Not Found"),
    ("DELETE", "/api/v1/countries/TestCountry", 404, "Delete Non-existent Country"),
]

results = []
for test in tests:
    results.append(test_endpoint(*test))

print(f"\n{'='*60}")
print(f"Test Summary: {sum(results)}/{len(results)} passed")
print(f"{'='*60}")
```

Run:
```bash
python test_api.py
```

---

## Postman Collection

Import this JSON into Postman:

```json
{
  "info": {
    "name": "Country Currency API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Refresh Countries",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/v1/countries/refresh"
      }
    },
    {
      "name": "Get All Countries",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/v1/countries"
      }
    },
    {
      "name": "Filter by Region",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/api/v1/countries?region=Africa",
          "query": [{"key": "region", "value": "Africa"}]
        }
      }
    },
    {
      "name": "Get Single Country",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/v1/countries/Nigeria"
      }
    },
    {
      "name": "Get Status",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/v1/status"
      }
    },
    {
      "name": "Get Summary Image",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/v1/countries/image"
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```

---

## Load Testing

Using Apache Bench:

```bash
# Test GET all countries
ab -n 1000 -c 10 http://localhost:8000/api/v1/countries

# Test status endpoint
ab -n 1000 -c 10 http://localhost:8000/api/v1/status
```

Using wrk:

```bash
# Install wrk
brew install wrk  # macOS
sudo apt install wrk  # Linux

# Run load test
wrk -t12 -c400 -d30s http://localhost:8000/api/v1/countries
```

---

## Automated Testing Checklist

- [ ] Health check responds
- [ ] Root endpoint returns metadata
- [ ] Refresh successfully loads data
- [ ] Get all countries returns array
- [ ] Region filter works correctly
- [ ] Currency filter works correctly
- [ ] Sorting works (all 4 options)
- [ ] Single country lookup works
- [ ] Case-insensitive name matching
- [ ] 404 for non-existent countries
- [ ] Delete works correctly
- [ ] Status shows correct counts
- [ ] Image generation works
- [ ] Image download works
- [ ] Error responses are consistent
- [ ] External API errors handled
- [ ] Database errors handled

---

## Performance Benchmarks

Target metrics:
- **Refresh**: < 30 seconds
- **Get all countries**: < 500ms
- **Get single country**: < 100ms
- **Status**: < 50ms
- **Image**: < 200ms

Monitor and optimize if metrics exceed targets.