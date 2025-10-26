from sqlalchemy import Column, Integer, String, BigInteger, DECIMAL, Text, TIMESTAMP, Index
from sqlalchemy.sql import func
from app.core.database import Base

class Country(Base):
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    capital = Column(String(255), nullable=True)
    region = Column(String(100), nullable=True, index=True)
    population = Column(BigInteger, nullable=False)
    currency_code = Column(String(10), nullable=True, index=True)
    exchange_rate = Column(DECIMAL(15, 6), nullable=True)
    estimated_gdp = Column(DECIMAL(20, 2), nullable=True)
    flag_url = Column(Text, nullable=True)
    last_refreshed_at = Column(TIMESTAMP, server_default=func.now())
    
    # Additional indexes for performance
    __table_args__ = (
        Index('idx_region_currency', 'region', 'currency_code'),
        Index('idx_estimated_gdp', 'estimated_gdp'),
    )
    
    def __repr__(self):
        return f"<Country(name={self.name}, region={self.region})>"