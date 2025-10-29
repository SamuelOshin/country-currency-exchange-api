from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal

class CountryBase(BaseModel):
    name: str
    capital: Optional[str] = None
    region: Optional[str] = None
    population: int
    currency_code: Optional[str] = None
    exchange_rate: Optional[float] = None
    estimated_gdp: Optional[float] = None
    flag_url: Optional[str] = None

class CountryResponse(CountryBase):
    id: int
    last_refreshed_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CountryListResponse(BaseModel):
    countries: list[CountryResponse]
    total: int