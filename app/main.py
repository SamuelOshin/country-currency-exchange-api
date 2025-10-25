from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as v1_router
from app.core.database import engine, Base
from app.core.config import settings
from app.utils.exceptions import (
    CountryNotFoundException, 
    ExternalAPIException, 
    ValidationException,
    ImageNotFoundException
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Country Currency & Exchange API",
    description="RESTful API for country data with currency exchange rates",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 router
app.include_router(v1_router.router, prefix="/api/v1")

# Global exception handlers
@app.exception_handler(CountryNotFoundException)
async def country_not_found_handler(request: Request, exc: CountryNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"error": "Country not found"}
    )

@app.exception_handler(ImageNotFoundException)
async def image_not_found_handler(request: Request, exc: ImageNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"error": "Summary image not found"}
    )

@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation failed",
            "details": exc.details
        }
    )

@app.exception_handler(ExternalAPIException)
async def external_api_exception_handler(request: Request, exc: ExternalAPIException):
    return JSONResponse(
        status_code=503,
        content={
            "error": "External data source unavailable",
            "details": f"Could not fetch data from {exc.api_name}"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Country Currency & Exchange API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "refresh": "POST /api/v1/countries/refresh",
            "countries": "GET /api/v1/countries",
            "country": "GET /api/v1/countries/{name}",
            "delete": "DELETE /api/v1/countries/{name}",
            "status": "GET /api/v1/status",
            "image": "GET /api/v1/countries/image"
        }
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.ENVIRONMENT == "development"
    )