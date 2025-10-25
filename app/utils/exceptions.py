class CountryNotFoundException(Exception):
    """Raised when a country is not found"""
    pass

class ExternalAPIException(Exception):
    """Raised when external API call fails"""
    def __init__(self, message: str, api_name: str):
        self.message = message
        self.api_name = api_name
        super().__init__(self.message)

class ValidationException(Exception):
    """Raised when validation fails"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)