# API Validation Scripts

This directory contains comprehensive validation scripts to test the Country Currency Exchange API against all HNGi13 requirements.

## Test Scripts

### 1. `test_validation_requirements.py` - Pytest Test Suite

Comprehensive pytest suite that validates all 7 requirement categories.

**Usage:**
```bash
# Run all validation tests
pytest tests/test_validation_requirements.py -v

# Run with detailed output
pytest tests/test_validation_requirements.py -v -s

# Run specific test category
pytest tests/test_validation_requirements.py -k "test_1" -v  # Test refresh endpoint
pytest tests/test_validation_requirements.py -k "test_2" -v  # Test filters & sorting
pytest tests/test_validation_requirements.py -k "test_3" -v  # Test get by name
```

**Features:**
- Uses pytest fixtures for database setup
- Tracks scores for each test
- Provides detailed summary at the end
- Tests against local test database

### 2. `validate_api.py` - Standalone Validation Script

Standalone script that tests against a live API endpoint without requiring pytest.

**Usage:**
```bash
# Test against local server (default: http://localhost:8000)
python validate_api.py

# Test against specific URL
python validate_api.py http://localhost:8000

# Test against deployed API
python validate_api.py https://your-api.com
```

**Features:**
- Color-coded output (✓ green for pass, ✗ red for fail)
- Tests against live API
- Detailed scoring breakdown
- No test database required
- Works with deployed APIs

## Test Categories (100 points total)

### TEST 1: POST /countries/refresh (25 points)
- ✓ Refresh endpoint accessible (3 pts)
- ✓ Returns correct status code (2 pts)
- ✓ Countries fetched and stored (100 countries) (5 pts)
- ✓ Currency codes properly stored (5 pts)
- ✓ Exchange rates calculated (5 pts)
- ✓ Estimated GDP calculated correctly (5 pts)

### TEST 2: GET /countries (filters & sorting) (25 points)
- ✓ Basic GET /countries works (5 pts)
- ✓ Returns correct structure (5 pts)
- ✓ Region filter works (5 pts)
- ✓ Currency filter works (5 pts)
- ✓ Sorting by GDP works (5 pts)

### TEST 3: GET /countries/:name (10 points)
- ✓ Get specific country works (5 pts)
- ✓ Returns correct country data (3 pts)
- ✓ Returns 404 for non-existent country (2 pts)

### TEST 4: DELETE /countries/:name (10 points)
- ✓ Delete endpoint works (5 pts)
- ✓ Country actually removed from database (3 pts)
- ✓ Returns 404 for deleting non-existent country (2 pts)

### TEST 5: GET /status (10 points)
- ✓ Status endpoint accessible (3 pts)
- ✓ Returns total_countries field (3 pts)
- ✓ Returns last_refreshed_at field (2 pts)
- ✓ Valid timestamp format (2 pts)

### TEST 6: GET /countries/image (10 points)
- ✓ Image endpoint accessible (3 pts)
- ✓ Correct Content-Type: image/png (3 pts)
- ✓ Returns image content (4 pts)

### TEST 7: Error Handling & Validation (10 points)
- ✓ 404 errors return proper JSON format (3 pts)
- ✓ Consistent error response structure (JSON) (4 pts)
- ✓ Error handling implemented (3 pts)

## Quick Start

### Option 1: Run Pytest Tests (Recommended for Development)

1. Ensure your virtual environment is activated:
   ```bash
   .\venv\Scripts\activate.ps1  # Windows PowerShell
   source venv/bin/activate      # Linux/Mac
   ```

2. Install test dependencies:
   ```bash
   pip install pytest
   ```

3. Run the validation tests:
   ```bash
   pytest tests/test_validation_requirements.py -v
   ```

### Option 2: Run Standalone Validation (For Live API Testing)

1. Ensure API is running:
   ```bash
   uvicorn app.main:app --reload
   ```

2. In a new terminal, run validation:
   ```bash
   python validate_api.py
   ```

## Expected Output

### Pytest Output
```
============================================================
TEST 1: POST /countries/refresh (25 points)
============================================================
✓ 1.1 Refresh endpoint accessible (3 pts)
✓ 1.2 Returns correct status code (2 pts)
✓ 1.3 Countries fetched and stored (100+ countries) (5 pts)
...
============================================================
FINAL RESULTS
============================================================
TOTAL SCORE: 100/100
============================================================
```

### Standalone Script Output
```
Starting API Validation
Base URL: http://localhost:8000
API Base: http://localhost:8000/api/v1
✓ API is accessible

============================================================
TEST 1: POST /countries/refresh (25 points)
============================================================
✓ 1.1 Refresh endpoint accessible (3/3 pts)
  Status: 200
✓ 1.2 Returns correct status code (2/2 pts)
...
============================================================
FINAL RESULTS
============================================================
TOTAL SCORE: 100/100 (100.0%)
============================================================
```

## Troubleshooting

### Common Issues

1. **API not accessible**
   - Ensure the API is running: `uvicorn app.main:app --reload`
   - Check the correct port (default: 8000)
   - Verify firewall settings

2. **Database errors**
   - Delete test database: `rm test.db`
   - Run migrations: `alembic upgrade head`

3. **Import errors**
   - Activate virtual environment
   - Install dependencies: `pip install -r requirements.txt`

4. **Test failures**
   - Check if database is populated: Run refresh endpoint first
   - Ensure external APIs are accessible
   - Check database connection settings

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# .github/workflows/test.yml
name: API Validation Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      - name: Run validation tests
        run: pytest tests/test_validation_requirements.py -v
```

## Contributing

When adding new tests:
1. Follow the existing naming convention: `test_X_Y_description`
2. Add proper docstrings explaining what is tested
3. Update scoring in the test results tracker
4. Ensure tests are idempotent (can run multiple times)

## License

Part of the HNGi13 Country Currency Exchange API project.
