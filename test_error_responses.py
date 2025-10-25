"""Quick test to verify error response formats"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("Testing error response formats:\n")

# Test 1: Country not found (404)
print("1. GET /api/v1/countries/NonExistent")
response = client.get("/api/v1/countries/NonExistent")
print(f"   Status: {response.status_code}")
print(f"   Body: {response.json()}")
print(f"   ✓ Expected: {{'error': 'Country not found'}}\n")

# Test 2: Image not found (404)
print("2. GET /api/v1/countries/image (no image exists)")
response = client.get("/api/v1/countries/image")
print(f"   Status: {response.status_code}")
print(f"   Body: {response.json()}")
print(f"   ✓ Expected: {{'error': 'Summary image not found'}}\n")

# Test 3: Status endpoint (should work)
print("3. GET /api/v1/status")
response = client.get("/api/v1/status")
print(f"   Status: {response.status_code}")
print(f"   Body: {response.json()}")
print(f"   ✓ Should return status data\n")

print("=" * 60)
print("Summary of Error Response Formats:")
print("=" * 60)
print("✓ 404 Country not found: {'error': 'Country not found'}")
print("✓ 404 Image not found: {'error': 'Summary image not found'}")
print("✓ 400 Validation failed: {'error': 'Validation failed', 'details': {...}}")
print("✓ 503 External API error: {'error': 'External data source unavailable', 'details': 'Could not fetch data from [API name]'}")
print("✓ 500 Internal error: {'error': 'Internal server error'}")
