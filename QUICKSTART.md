# Quick Start Guide

Get the Country Currency API running in 5 minutes.

## Prerequisites

- Python 3.11+
- MySQL 8.0+
- Git

## Installation Steps

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd country-currency-api
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up MySQL Database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE countries_db;
EXIT;
```

### 5. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/countries_db
```

### 6. Run Migrations

```bash
alembic upgrade head
```

### 7. Start Server

```bash
uvicorn app.main:app --reload
```

Server running at: `http://localhost:8000`

### 8. Load Initial Data

```bash
curl -X POST http://localhost:8000/api/v1/countries/refresh
```

Wait ~20-30 seconds for data to load.

### 9. Test API

```bash
# Get all countries
curl http://localhost:8000/api/v1/countries

# Get African countries
curl "http://localhost:8000/api/v1/countries?region=Africa"

# Get status
curl http://localhost:8000/api/v1/status

# View docs
open http://localhost:8000/docs
```

## Using Docker (Alternative)

```bash
# Start services
docker-compose up -d

# Wait for services to be healthy
docker-compose ps

# Load initial data
curl -X POST http://localhost:8000/api/v1/countries/refresh
```

## Verify Installation

✅ Server responds: `http://localhost:8000/health`  
✅ Docs accessible: `http://localhost:8000/docs`  
✅ Countries loaded: `http://localhost:8000/api/v1/status`  
✅ Image generated: `http://localhost:8000/api/v1/countries/image`

## Common Issues

### Database Connection Error
```bash
# Check MySQL is running
sudo systemctl status mysql  # Linux
brew services list  # macOS

# Verify credentials in .env
```

### Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### External API Timeout
```bash
# Increase timeout in .env
API_TIMEOUT=60

# Check internet connection
curl https://restcountries.com/v2/all
```

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- Check [API_TESTING.md](API_TESTING.md) for testing guide
- See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment options
- Explore API at `http://localhost:8000/docs`

## Support

For issues, check:
1. Application logs
2. Database connection
3. Environment variables
4. External API accessibility

Happy coding! 🚀