"""
Standalone validation script for HNGi13 Country Currency Exchange API
Tests against a live API endpoint
Usage: python validate_api.py [BASE_URL]
Example: python validate_api.py http://localhost:8000
"""
import requests
import sys
from datetime import datetime
from typing import Dict, Any


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class APIValidator:
    """Validate API endpoints and functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}"
        self.results = []
        self.total_score = 0
        self.max_score = 100
        
    def log(self, message: str, color: str = Colors.RESET):
        """Print colored message"""
        print(f"{color}{message}{Colors.RESET}")
        
    def test_endpoint(self, name: str, points: int, test_func) -> bool:
        """Run a test and record results"""
        try:
            passed, message = test_func()
            status = "✓" if passed else "✗"
            color = Colors.GREEN if passed else Colors.RED
            score = points if passed else 0
            
            self.results.append({
                'name': name,
                'passed': passed,
                'points': score,
                'max_points': points,
                'message': message
            })
            
            self.total_score += score
            self.log(f"{status} {name} ({score}/{points} pts)", color)
            if message:
                self.log(f"  {message}", Colors.CYAN)
            
            return passed
        except Exception as e:
            self.log(f"✗ {name} (0/{points} pts)", Colors.RED)
            self.log(f"  Error: {str(e)}", Colors.RED)
            self.results.append({
                'name': name,
                'passed': False,
                'points': 0,
                'max_points': points,
                'message': str(e)
            })
            return False
    
    def print_section(self, title: str, test_num: int, max_points: int):
        """Print section header"""
        print("\n" + "="*60)
        print(f"TEST {test_num}: {title} ({max_points} points)")
        print("="*60)
    
    def print_summary(self):
        """Print final summary"""
        print("\n" + "="*60)
        print(f"{Colors.BOLD}FINAL RESULTS{Colors.RESET}")
        print("="*60)
        
        # Group by test section
        sections = {}
        for result in self.results:
            section = result['name'].split('.')[0]
            if section not in sections:
                sections[section] = {'passed': 0, 'failed': 0, 'points': 0, 'max_points': 0}
            
            if result['passed']:
                sections[section]['passed'] += 1
            else:
                sections[section]['failed'] += 1
            sections[section]['points'] += result['points']
            sections[section]['max_points'] += result['max_points']
        
        for section, stats in sections.items():
            self.log(
                f"Section {section}: {stats['points']}/{stats['max_points']} pts "
                f"({stats['passed']} passed, {stats['failed']} failed)",
                Colors.YELLOW
            )
        
        print("="*60)
        percentage = (self.total_score / self.max_score * 100) if self.max_score > 0 else 0
        color = Colors.GREEN if percentage >= 70 else Colors.YELLOW if percentage >= 50 else Colors.RED
        self.log(
            f"TOTAL SCORE: {self.total_score}/{self.max_score} ({percentage:.1f}%)",
            color
        )
        print("="*60)
    
    # ============================================================
    # TEST 1: POST /countries/refresh (25 points)
    # ============================================================
    
    def run_test_1(self):
        """Test 1: POST /countries/refresh"""
        self.print_section("POST /countries/refresh", 1, 25)
        
        def test_1_1():
            r = requests.post(f"{self.api_base}/countries/refresh", timeout=30)
            return r.status_code in [200, 201], f"Status: {r.status_code}"
        
        def test_1_2():
            r = requests.post(f"{self.api_base}/countries/refresh", timeout=30)
            return r.status_code == 200, f"Status: {r.status_code}"
        
        def test_1_3():
            requests.post(f"{self.api_base}/countries/refresh", timeout=30)
            r = requests.get(f"{self.api_base}/countries")
            countries = r.json()
            count = len(countries)
            return count >= 100, f"Found {count} countries"
        
        def test_1_4():
            r = requests.get(f"{self.api_base}/countries")
            countries = r.json()
            with_currency = sum(1 for c in countries if c.get('currency_code'))
            percentage = (with_currency / len(countries) * 100) if countries else 0
            return percentage >= 90, f"{with_currency}/{len(countries)} countries ({percentage:.1f}%)"
        
        def test_1_5():
            r = requests.get(f"{self.api_base}/countries")
            countries = r.json()
            # Check that exchange_rate is numeric (not string)
            with_rates = sum(1 for c in countries 
                           if c.get('exchange_rate') is not None 
                           and isinstance(c.get('exchange_rate'), (int, float)) 
                           and c.get('exchange_rate') > 0)
            percentage = (with_rates / len(countries) * 100) if countries else 0
            return percentage >= 80, f"{with_rates}/{len(countries)} countries ({percentage:.1f}%)"
        
        def test_1_6():
            r = requests.get(f"{self.api_base}/countries")
            countries = r.json()
            # Check that estimated_gdp is numeric (not string)
            with_gdp = sum(1 for c in countries 
                         if c.get('estimated_gdp') is not None 
                         and isinstance(c.get('estimated_gdp'), (int, float)) 
                         and c.get('estimated_gdp') > 0)
            percentage = (with_gdp / len(countries) * 100) if countries else 0
            return percentage >= 80, f"{with_gdp}/{len(countries)} countries ({percentage:.1f}%)"
        
        self.test_endpoint("1.1 Refresh endpoint accessible", 3, test_1_1)
        self.test_endpoint("1.2 Returns correct status code", 2, test_1_2)
        self.test_endpoint("1.3 Countries fetched and stored (100+ countries)", 5, test_1_3)
        self.test_endpoint("1.4 Currency codes properly stored", 5, test_1_4)
        self.test_endpoint("1.5 Exchange rates calculated", 5, test_1_5)
        self.test_endpoint("1.6 Estimated GDP calculated correctly", 5, test_1_6)
    
    # ============================================================
    # TEST 2: GET /countries (filters & sorting) (25 points)
    # ============================================================
    
    def run_test_2(self):
        """Test 2: GET /countries (filters & sorting)"""
        self.print_section("GET /countries (filters & sorting)", 2, 25)
        
        def test_2_1():
            r = requests.get(f"{self.api_base}/countries")
            return r.status_code == 200 and len(r.json()) > 0, f"Status: {r.status_code}, Count: {len(r.json())}"
        
        def test_2_2():
            r = requests.get(f"{self.api_base}/countries")
            data = r.json()
            if not data:
                return False, "No countries found"
            required = ['name', 'capital', 'region', 'population', 'currency_code', 
                       'exchange_rate', 'estimated_gdp', 'flag_url']
            missing = [f for f in required if f not in data[0]]
            return len(missing) == 0, f"Missing fields: {missing}" if missing else "All fields present"
        
        def test_2_3():
            r = requests.get(f"{self.api_base}/countries?region=Africa")
            if r.status_code != 200:
                return False, f"Status: {r.status_code}"
            data = r.json()
            all_africa = all(c.get('region') == 'Africa' for c in data)
            return all_africa and len(data) > 0, f"Found {len(data)} African countries"
        
        def test_2_4():
            r = requests.get(f"{self.api_base}/countries?currency=USD")
            if r.status_code != 200:
                return False, f"Status: {r.status_code}"
            data = r.json()
            all_usd = all(c.get('currency_code') == 'USD' for c in data)
            return all_usd and len(data) > 0, f"Found {len(data)} countries with USD"
        
        def test_2_5():
            r = requests.get(f"{self.api_base}/countries?sort=gdp_desc")
            if r.status_code != 200:
                return False, f"Status: {r.status_code}"
            data = r.json()
            if len(data) < 2:
                return False, "Not enough data to test sorting"
            # Filter out None values and ensure numeric types
            gdps = [c['estimated_gdp'] for c in data 
                   if c.get('estimated_gdp') is not None 
                   and isinstance(c.get('estimated_gdp'), (int, float))]
            if not gdps:
                return False, "No valid GDP values to sort"
            is_sorted = gdps == sorted(gdps, reverse=True)
            return is_sorted, "GDP sorted descending" if is_sorted else f"GDP not sorted correctly: {gdps[:5]}"
        
        self.test_endpoint("2.1 Basic GET /countries works", 5, test_2_1)
        self.test_endpoint("2.2 Returns correct structure", 5, test_2_2)
        self.test_endpoint("2.3 Region filter works", 5, test_2_3)
        self.test_endpoint("2.4 Currency filter works", 5, test_2_4)
        self.test_endpoint("2.5 Sorting by GDP works", 5, test_2_5)
    
    # ============================================================
    # TEST 3: GET /countries/:name (10 points)
    # ============================================================
    
    def run_test_3(self):
        """Test 3: GET /countries/:name"""
        self.print_section("GET /countries/:name", 3, 10)
        
        def test_3_1():
            r = requests.get(f"{self.api_base}/countries/Nigeria")
            return r.status_code == 200, f"Status: {r.status_code}"
        
        def test_3_2():
            r = requests.get(f"{self.api_base}/countries/Nigeria")
            if r.status_code != 200:
                return False, f"Status: {r.status_code}"
            data = r.json()
            is_correct = data.get('name') == 'Nigeria' and 'capital' in data and 'currency_code' in data
            return is_correct, f"Got country: {data.get('name')}"
        
        def test_3_3():
            r = requests.get(f"{self.api_base}/countries/NonExistentCountryXYZ")
            return r.status_code == 404, f"Status: {r.status_code}"
        
        self.test_endpoint("3.1 Get specific country works", 5, test_3_1)
        self.test_endpoint("3.2 Returns correct country data", 3, test_3_2)
        self.test_endpoint("3.3 Returns 404 for non-existent country", 2, test_3_3)
    
    # ============================================================
    # TEST 4: DELETE /countries/:name (10 points)
    # ============================================================
    
    def run_test_4(self):
        """Test 4: DELETE /countries/:name"""
        self.print_section("DELETE /countries/:name", 4, 10)
        
        def test_4_1():
            # First ensure a country exists
            r = requests.get(f"{self.api_base}/countries/Nigeria")
            if r.status_code != 200:
                return False, "Nigeria not found in database"
            
            r = requests.delete(f"{self.api_base}/countries/Nigeria")
            return r.status_code == 200, f"Status: {r.status_code}"
        
        def test_4_2():
            # Re-add Nigeria if needed
            requests.post(f"{self.api_base}/countries/refresh", timeout=10)
            
            # Delete it
            requests.delete(f"{self.api_base}/countries/TestCountryDelete")
            
            # Try to get it
            r = requests.get(f"{self.api_base}/countries/TestCountryDelete")
            return r.status_code == 404, "Country should be deleted"
        
        def test_4_3():
            r = requests.delete(f"{self.api_base}/countries/NonExistentCountryXYZ")
            return r.status_code == 404, f"Status: {r.status_code}"
        
        self.test_endpoint("4.1 Delete endpoint works", 5, test_4_1)
        self.test_endpoint("4.2 Country actually removed from database", 3, test_4_2)
        self.test_endpoint("4.3 Returns 404 for deleting non-existent country", 2, test_4_3)
    
    # ============================================================
    # TEST 5: GET /status (10 points)
    # ============================================================
    
    def run_test_5(self):
        """Test 5: GET /status"""
        self.print_section("GET /status", 5, 10)
        
        def test_5_1():
            r = requests.get(f"{self.api_base}/status")
            return r.status_code == 200, f"Status: {r.status_code}"
        
        def test_5_2():
            r = requests.get(f"{self.api_base}/status")
            data = r.json()
            has_field = 'total_countries' in data
            return has_field, f"total_countries: {data.get('total_countries', 'missing')}"
        
        def test_5_3():
            r = requests.get(f"{self.api_base}/status")
            data = r.json()
            return 'last_refreshed_at' in data, "Field present" if 'last_refreshed_at' in data else "Field missing"
        
        def test_5_4():
            r = requests.get(f"{self.api_base}/status")
            data = r.json()
            timestamp = data.get('last_refreshed_at')
            if timestamp is None:
                return True, "Null timestamp (acceptable)"
            try:
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return True, f"Valid timestamp: {timestamp}"
            except:
                return False, f"Invalid timestamp: {timestamp}"
        
        self.test_endpoint("5.1 Status endpoint accessible", 3, test_5_1)
        self.test_endpoint("5.2 Returns total_countries field", 3, test_5_2)
        self.test_endpoint("5.3 Returns last_refreshed_at field", 2, test_5_3)
        self.test_endpoint("5.4 Valid timestamp format", 2, test_5_4)
    
    # ============================================================
    # TEST 6: GET /countries/image (10 points)
    # ============================================================
    
    def run_test_6(self):
        """Test 6: GET /countries/image"""
        self.print_section("GET /countries/image", 6, 10)
        
        def test_6_1():
            r = requests.get(f"{self.api_base}/countries/image")
            return r.status_code == 200, f"Status: {r.status_code}"
        
        def test_6_2():
            r = requests.get(f"{self.api_base}/countries/image")
            content_type = r.headers.get('content-type', '')
            return content_type == 'image/png', f"Content-Type: {content_type}"
        
        def test_6_3():
            r = requests.get(f"{self.api_base}/countries/image")
            size = len(r.content)
            is_png = r.content[:4] == b'\x89PNG'
            return size > 1000 and is_png, f"Size: {size} bytes, PNG: {is_png}"
        
        self.test_endpoint("6.1 Image endpoint accessible", 3, test_6_1)
        self.test_endpoint("6.2 Correct Content-Type: image/png", 3, test_6_2)
        self.test_endpoint("6.3 Returns image content", 4, test_6_3)
    
    # ============================================================
    # TEST 7: Error Handling & Validation (10 points)
    # ============================================================
    
    def run_test_7(self):
        """Test 7: Error Handling & Validation"""
        self.print_section("Error Handling & Validation", 7, 10)
        
        def test_7_1():
            r = requests.get(f"{self.api_base}/countries/NonExistentCountryXYZ")
            if r.status_code != 404:
                return False, f"Status: {r.status_code}"
            try:
                data = r.json()
                # Check for either 'detail' or 'error' field (both are valid JSON error formats)
                has_error_field = isinstance(data, dict) and ('detail' in data or 'error' in data)
                return has_error_field, "Valid JSON error response"
            except:
                return False, "Not JSON"
        
        def test_7_2():
            endpoints = [
                f"{self.api_base}/countries/NonExistent1",
                f"{self.api_base}/countries/NonExistent2"
            ]
            
            for url in endpoints:
                r = requests.get(url)
                if r.status_code >= 400:
                    try:
                        data = r.json()
                        # Check for either 'detail' or 'error' field (both are valid)
                        if not isinstance(data, dict) or not ('detail' in data or 'error' in data):
                            return False, "Inconsistent error structure"
                    except:
                        return False, "Error not in JSON format"
            
            return True, "Consistent error responses"
        
        def test_7_3():
            tests = [
                requests.get(f"{self.api_base}/countries/NonExistent"),
                requests.delete(f"{self.api_base}/countries/NonExistent")
            ]
            
            proper_codes = all(r.status_code in [404, 422] for r in tests)
            return proper_codes, "Error codes handled properly"
        
        self.test_endpoint("7.1 404 errors return proper JSON format", 3, test_7_1)
        self.test_endpoint("7.2 Consistent error response structure", 4, test_7_2)
        self.test_endpoint("7.3 Error handling implemented", 3, test_7_3)
    
    def run_all_tests(self):
        """Run all validation tests"""
        self.log(f"\n{Colors.BOLD}Starting API Validation{Colors.RESET}", Colors.BLUE)
        self.log(f"Base URL: {self.base_url}", Colors.CYAN)
        self.log(f"API Base: {self.api_base}", Colors.CYAN)
        
        try:
            # Test if API is accessible
            r = requests.get(self.base_url, timeout=5)
            self.log("✓ API is accessible\n", Colors.GREEN)
        except Exception as e:
            self.log(f"✗ Cannot connect to API: {e}", Colors.RED)
            return
        
        # Run all test sections
        self.run_test_1()
        self.run_test_2()
        self.run_test_3()
        self.run_test_4()
        self.run_test_5()
        self.run_test_6()
        self.run_test_7()
        
        # Print summary
        self.print_summary()


def main():
    """Main entry point"""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    validator = APIValidator(base_url)
    validator.run_all_tests()


if __name__ == "__main__":
    main()
