import random
from decimal import Decimal
from typing import Optional

def generate_random_multiplier() -> int:
    """Generate random multiplier between 1000 and 2000"""
    return random.randint(1000, 2000)

def calculate_gdp(population: int, exchange_rate: Optional[Decimal]) -> Optional[Decimal]:
    """
    Calculate estimated GDP: population × random(1000–2000) ÷ exchange_rate
    
    Returns:
        - Decimal if exchange_rate is valid
        - None if exchange_rate is None
        - 0 if exchange_rate is 0 or population is 0
    """
    if exchange_rate is None:
        return None
    
    if population == 0 or exchange_rate == 0:
        return Decimal("0")
    
    multiplier = generate_random_multiplier()
    gdp = (Decimal(population) * Decimal(multiplier)) / exchange_rate
    return round(gdp, 2)

def normalize_country_name(name: str) -> str:
    """Normalize country name for comparison (lowercase, stripped)"""
    return name.strip().lower()