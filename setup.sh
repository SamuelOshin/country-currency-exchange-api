#!/bin/bash

echo "🚀 Setting up Country Currency API..."

# Detect OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    OS="windows"
    PYTHON_CMD="python"
else
    OS="unix"
    PYTHON_CMD="python3"
fi

echo "✓ Detected OS: $(echo $OS | tr '[:lower:]' '[:upper:]')"

# Check Python version
python_version=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment (check if it doesn't already exist)
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
if [[ "$OS" == "windows" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file (check if it doesn't already exist)
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "📝 Creating .env file from .env.example..."
        cp .env.example .env
        echo "⚠️  Please edit .env with your database credentials"
    else
        echo "❌ .env.example not found!"
    fi
else
    echo "✓ .env file already exists (skipping creation)"
fi

# Create cache directory (check if it doesn't already exist)
if [ ! -d "app/cache" ]; then
    echo "📁 Creating cache directory..."
    mkdir -p app/cache
else
    echo "✓ Cache directory already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your database credentials"
echo "2. Create MySQL database: CREATE DATABASE countries_db;"
echo "3. Run migrations: alembic upgrade head"
echo "4. Start server: uvicorn app.main:app --reload"
echo "5. Load initial data: curl -X POST http://localhost:8000/api/v1/countries/refresh"
echo ""
echo "📚 Documentation: http://localhost:8000/docs"