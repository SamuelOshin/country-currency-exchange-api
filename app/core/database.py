from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os
import ssl

# Get absolute path to CA certificate
ca_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), settings.SSL_CERT_PATH)

# Verify CA certificate exists
if not os.path.exists(ca_path):
    raise FileNotFoundError(f"CA certificate not found at {ca_path}")

# Create SSL context for PyMySQL
ssl_context = ssl.create_default_context(cafile=ca_path)
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

# Create SQLAlchemy engine with SSL context
connect_args = {
    'ssl': ssl_context,
}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.ENVIRONMENT == "development"
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()