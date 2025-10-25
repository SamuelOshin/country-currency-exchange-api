# Country Currency & Exchange API

A RESTful API that fetches country data from external APIs, enriches it with exchange rates, and provides CRUD operations with caching in MySQL.

## Features

- ✅ Fetch and cache country data from restcountries.com
- ✅ Integrate real-time exchange rates from open.er-api.com
- ✅ Calculate estimated GDP for each country
- ✅ Filter and sort countries by region, currency, and GDP
- ✅ Generate summary images with statistics
- ✅ Full CRUD operations
- ✅ MySQL database caching
- ✅ Comprehensive error handling

## Tech Stack

- **Framework**: FastAPI
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Image Processing**: Pillow
- **HTTP Client**: httpx
- **Python**: 3.11+

## Project Structure

```
country-currency-api/
├── app/
│   ├── main.py                    # Application entry point
│   ├── core/                      # Core configurations
│   │   ├── config.py              # Settings
│   │   ├── database.py            # Database setup
│   │   └── dependencies.py        # Dependencies
│   ├── api/
│   │   └── v1/                    # API Version 1
│   │       ├── models/            # SQLAlchemy models
│   │       ├── schemas/           # Pydantic schemas
│   │       ├── repositories/      # Data access layer
│   │       ├── services/          # Business logic
│   │       ├── routes/            # API endpoints
│   │       └── router.py          # Route aggregator
│   ├── utils/                     # Helper utilities
│   └── cache/                     # Cache directory for images
├── alembic/                       # Database migrations
├── tests/                         # Test suite
├── requirements.txt               # Python dependencies
├── .env.example                   # Example environment variables
├── docker-compose.yml             # Docker setup
└── README.md
```

## API Endpoints

### 1. Refresh Countries Cache
```http
POST /api/v1/countries/refresh
```
Fetches data from external APIs and updates the database cache.

**Response:**
```json
{
  "message": "Countries refreshed successfully",
  "countries_processed": 250,
  "total_countries": 250,
  "last_refreshed_at": "2025-10-25T18:00:00Z"
}
```

### 2. Get All Countries
```http
GET /api/v1/countries
GET /api/v1/countries?region=Africa
GET /api/v1/countries?currency=NGN
GET /api/v1/countries?sort=gdp_desc
GET /api/v1/countries?region=Africa&sort=gdp_desc
```

**Response:**
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
    "last_refreshed_at": "2025-10-25T18:00:00Z"
  }
]
```

### 3. Get Single Country
```http
GET /api/v1/countries/{name}
```

**Example:**
```http
GET /api/v1/countries/Nigeria
```

### 4. Delete Country
```http
DELETE /api/v1/countries/{name}
```

**Response:**
```json
{
  "message": "Country 'Nigeria' deleted successfully"
}
```

### 5. Get Status
```http
GET /api/v1/status
```

**Response:**
```json
{
  "total_countries": 250,
  "last_refreshed_at": "2025-10-25T18:00:00Z"
}
```

### 6. Get Summary Image
```http
GET /api/v1/countries/image
```
Returns a PNG image with:
- Total countries count
- Top 5 countries by GDP
- Last refresh timestamp

## Installation & Setup

### Prerequisites

- Python 3.11+
- MySQL 8.0+
- pip

### Option 1: Local Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd country-currency-api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up MySQL database**
```bash
mysql -u root -p
CREATE DATABASE countries_db;
```

5. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/countries_db
API_HOST=0.0.0.0
API_PORT=8000
RESTCOUNTRIES_API_URL=https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies
EXCHANGE_API_URL=https://open.er-api.com/v6/latest/USD
API_TIMEOUT=30
CACHE_DIR=app/cache
ENVIRONMENT=development
```

6. **Run database migrations**
```bash
alembic upgrade head
```

7. **Start the server**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

8. **Initial data load**
```bash
curl -X POST http://localhost:8000/api/v1/countries/refresh
```

### Option 2: Docker Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd country-currency-api
```

2. **Start with Docker Compose**
```bash
docker-compose up -d
```

3. **Initial data load**
```bash
curl -X POST http://localhost:8000/api/v1/countries/refresh
```

## Usage Examples

### Using cURL

**Refresh data:**
```bash
curl -X POST http://localhost:8000/api/v1/countries/refresh
```

**Get all African countries:**
```bash
curl "http://localhost:8000/api/v1/countries?region=Africa"
```

**Get countries sorted by GDP:**
```bash
curl "http://localhost:8000/api/v1/countries?sort=gdp_desc"
```

**Get a specific country:**
```bash
curl http://localhost:8000/api/v1/countries/Nigeria
```

**Delete a country:**
```bash
curl -X DELETE http://localhost:8000/api/v1/countries/Nigeria
```

**Get status:**
```bash
curl http://localhost:8000/api/v1/status
```

**Download summary image:**
```bash
curl http://localhost:8000/api/v1/countries/image --output summary.png
```

### Using Python

```python
import requests

# Refresh data
response = requests.post("http://localhost:8000/api/v1/countries/refresh")
print(response.json())

# Get African countries
response = requests.get("http://localhost:8000/api/v1/countries", 
                       params={"region": "Africa", "sort": "gdp_desc"})
countries = response.json()

# Get single country
response = requests.get("http://localhost:8000/api/v1/countries/Nigeria")
nigeria = response.json()
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | MySQL connection string | Required |
| `API_HOST` | Server host | `0.0.0.0` |
| `API_PORT` | Server port | `8000` |
| `RESTCOUNTRIES_API_URL` | Countries API URL | Required |
| `EXCHANGE_API_URL` | Exchange rates API URL | Required |
| `API_TIMEOUT` | API request timeout (seconds) | `30` |
| `CACHE_DIR` | Cache directory path | `app/cache` |
| `ENVIRONMENT` | Environment (development/production) | `development` |

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

The API returns consistent JSON error responses:

**404 Not Found:**
```json
{
  "error": "Country not found"
}
```

**400 Bad Request:**
```json
{
  "error": "Validation failed",
  "details": {
    "currency_code": "is required"
  }
}
```

**503 Service Unavailable:**
```json
{
  "error": "External data source unavailable",
  "details": "Could not fetch data from restcountries.com"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error"
}
```

## Data Processing Logic

### Currency Handling

1. **Multiple currencies**: Only the first currency is stored
2. **No currencies**: 
   - `currency_code`: `null`
   - `exchange_rate`: `null`
   - `estimated_gdp`: `0`
3. **Currency not in exchange rates**:
   - `exchange_rate`: `null`
   - `estimated_gdp`: `null`

### GDP Calculation

```
estimated_gdp = (population × random(1000-2000)) ÷ exchange_rate
```

A fresh random multiplier is generated on each refresh for every country.

### Update Logic

Countries are matched by name (case-insensitive):
- **If exists**: Update all fields with new data
- **If new**: Insert as new record

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Deployment

### Railway (Recommended)

1. Create a new project on Railway
2. Add MySQL database service
3. Connect GitHub repository
4. Set environment variables
5. Deploy

### Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add MySQL addon
heroku addons:create jawsdb:kitefin

# Set environment variables
heroku config:set ENVIRONMENT=production

# Deploy
git push heroku main

# Run initial refresh
curl -X POST https://your-app-name.herokuapp.com/api/v1/countries/refresh
```

### AWS / DigitalOcean

1. Set up MySQL RDS/Droplet
2. Deploy FastAPI app to EC2/Droplet
3. Configure environment variables
4. Use Nginx as reverse proxy
5. Set up SSL with Let's Encrypt

## Troubleshooting

### Database Connection Issues
```bash
# Check MySQL is running
mysql -u root -p

# Verify DATABASE_URL format
mysql+pymysql://user:password@host:port/database
```

### External API Timeouts
- Increase `API_TIMEOUT` in `.env`
- Check internet connectivity
- Verify API URLs are accessible

### Image Generation Fails
```bash
# Install fonts on Linux
sudo apt-get install fonts-dejavu-core

# On macOS
brew install font-dejavu
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Author

Your Name - your.email@example.com

## Acknowledgments

- [RestCountries API](https://restcountries.com/)
- [Open Exchange Rates API](https://open.er-api.com/)
- [FastAPI](https://fastapi.tiangolo.com/)