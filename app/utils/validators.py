from app.utils.exceptions import ValidationException

def validate_country_data(name: str, population: int, currency_code: str = None):
    """
    Validate country data according to task requirements
    
    Required fields:
    - name
    - population
    - currency_code (can be None for countries without currency)
    """
    errors = {}
    
    if not name or not name.strip():
        errors["name"] = "is required"
    
    if population is None:
        errors["population"] = "is required"
    elif not isinstance(population, int) or population < 0:
        errors["population"] = "must be a non-negative integer"
    
    # Note: currency_code is required but can be None for countries without currency
    # This is validated in the business logic layer
    
    if errors:
        raise ValidationException("Validation failed", details=errors)