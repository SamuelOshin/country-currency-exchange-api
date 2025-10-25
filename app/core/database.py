import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os
import ssl
import base64
import tempfile

# Configure logger
logger = logging.getLogger(__name__)

# Configure SSL based on settings
connect_args = {}

# Check if certificate is provided as base64 in environment variable
ssl_cert_base64 = os.getenv('SSL_CERT_BASE64')

if ssl_cert_base64:
    # Decode base64 certificate and write to temporary file
    try:
        cert_content = base64.b64decode(ssl_cert_base64)
        # Create temporary file for certificate
        temp_cert = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pem')
        temp_cert.write(cert_content)
        temp_cert.close()
        ca_path = temp_cert.name
        
        # Create SSL context with the decoded certificate
        ssl_context = ssl.create_default_context(cafile=ca_path)
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        connect_args['ssl'] = ssl_context
        logger.info("Using SSL with certificate from environment variable")
    except Exception as e:
        logger.warning(f"Failed to decode SSL certificate from environment: {e}")
        # Fallback to required SSL without verification
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args['ssl'] = ssl_context

elif settings.SSL_VERIFY and settings.SSL_CERT_PATH:
    # Get absolute path to CA certificate file
    ca_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), settings.SSL_CERT_PATH)
    
    # Check if certificate file exists
    if os.path.exists(ca_path):
        # Create SSL context for PyMySQL
        ssl_context = ssl.create_default_context(cafile=ca_path)
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        connect_args['ssl'] = ssl_context
        logger.info(f"Using SSL with certificate file: {ca_path}")
    else:
        logger.warning(f"SSL certificate not found at {ca_path}")
        # For databases that require SSL, use SSL without verification as fallback
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args['ssl'] = ssl_context
        logger.info("Using SSL without certificate verification")
else:
    # No certificate provided, but Aiven requires SSL
    # Use SSL with system's default CA certificates
    logger.info("Using SSL with system CA certificates")
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    connect_args['ssl'] = ssl_context

# Create SQLAlchemy engine
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